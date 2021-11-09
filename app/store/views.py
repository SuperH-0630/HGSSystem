from flask import render_template, Blueprint, Flask, redirect, url_for, abort, flash
from wtforms import StringField, SubmitField
from flask_login import current_user
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from conf import Config
from tool.typing import Optional
from app import views

from app.auth import views as auth_views

store = Blueprint("store", __name__)
app: Optional[Flask] = None


class BuySetForm(FlaskForm):
    """
    兑换/库存设定/积分设定表单
    """
    quantity = StringField(validators=[DataRequired(message="请输入数量")])
    submit = SubmitField()


class AddNewGoodsForm(FlaskForm):
    """
    新增商品表单
    """
    name = StringField(validators=[DataRequired(message="请输入名字")])
    quantity = StringField(validators=[DataRequired(message="请输入库存")])
    score = StringField(validators=[DataRequired(message="请输入库存")])
    submit = SubmitField()


@store.route('/', methods=['GET', 'POST'])
@auth_views.web_user_required
def index():
    """
    显示购买的表单
    购买时发送请求到 store.buy
    :return:
    """
    form = BuySetForm()
    store_list = views.website.get_store_list()
    return render_template("store/store.html", store_list=store_list, store_form=form)


@store.route('/buy/<int:goods_id>', methods=['POST'])
@auth_views.web_user_required
def buy(goods_id: int):
    """
    处理购买的表单
    仅支持 Post 请求
    非表单的一律 404
    """
    form = BuySetForm()
    if form.validate_on_submit():
        try:
            quantity = int(form.quantity.data)
        except (TypeError, ValueError):
            flash("请输入正确的数量")
        else:
            goods = views.website.get_goods(goods_id)
            if goods is None:
                flash("商品错误")
            res, order_id = goods.buy_for_user(quantity, current_user)
            if res == -1:
                flash("用户不支持兑换商品")
            elif res == -2:
                flash("兑换数目超出库存")
            elif res == -3:
                flash("积分不足")
            elif res == -5:
                flash("用户登录冲突")
            elif res == 0:
                flash(f"商品兑换成功, 订单: {order_id}")
            else:
                flash("未知错误")
            return redirect(url_for("store.index"))
    abort(404)


@store.route('/set/<int:goods_id>', methods=['POST'])
@auth_views.manager_required
def set_goods(goods_id: int):
    """
    设置库存
    仅支持 Post 请求
    非表单的一律 404
    """
    form = BuySetForm()
    if form.validate_on_submit():
        try:
            quantity = int(form.quantity.data)
        except (TypeError, ValueError):
            flash("请输入正确的数量")
        else:
            if not views.website.set_goods_quantity(quantity, goods_id):
                abort(404)
            return redirect(url_for("store.index"))
    abort(404)


@store.route('/set_score/<int:goods_id>', methods=['POST'])
@auth_views.manager_required
def set_goods_score(goods_id: int):
    """
    设置兑换积分
    仅支持 Post 请求
    非表单的一律 404
    """
    form = BuySetForm()
    if form.validate_on_submit():
        try:
            score = int(form.quantity.data)
        except (TypeError, ValueError):
            flash("请输入正确的数量")
        else:
            if not views.website.set_goods_score(score, goods_id):
                abort(404)
            return redirect(url_for("store.index"))
    abort(404)


@store.route('/check/<string:user>/<string:order>')
@auth_views.manager_required
def check(user, order):
    """
    显示取件码的获取内容
    """
    res, uid = views.website.check_order(order, user)
    if res is None:
        abort(404)
    return render_template("store/goods.html", goods_list=res, goods_user=uid[:Config.show_uid_len], order_id=order)


@store.route('/confirm/<string:token>')
@auth_views.manager_required
def confirm(token):
    """
    确认取件
    """
    try:
        s = Serializer(Config.passwd_salt)
        data = s.loads(token)
        order = data["order"]
        user = data["uid"]
    except:
        abort(404)
    else:
        if not views.website.confirm_order(order, user):
            abort(404)
        flash(f"订单: {order} 处理成功")
    return redirect(url_for("hello.index"))


@store.route('/add', methods=["GET", "POST"])
@auth_views.manager_required
def add_new_goods():
    """
    新增新商品
    """
    form = AddNewGoodsForm()
    if form.validate_on_submit():
        name = form.name.data
        score = form.score.data
        quantity = form.quantity.data
        if not views.website.add_new_goods(name, score, quantity):
            abort(404)
        flash(f"新增商品 {name} 成功")
        return redirect(url_for("store.add_new_goods"))
    return render_template("store/add.html", add_form=form)


def creat_store_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(store, url_prefix="/store")
