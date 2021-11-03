from flask import render_template, Blueprint, Flask, redirect, url_for, abort, flash
from wtforms import TextField, SubmitField
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_login import login_required
import functools

from tool.type_ import Optional
from app import views
from app import web_user

store = Blueprint("store", __name__)
app: Optional[Flask] = None


class BuyForm(FlaskForm):
    quantity = TextField()
    submit = SubmitField()


@store.route('/buy/<int:goods_id>', methods=['GET', 'POST'])
@login_required
def buy(goods_id: int):
    form = BuyForm()
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
            elif res == 0:
                flash(f"商品兑换成功, 订单: {order_id}")
            else:
                flash("未知错误")
            return redirect(url_for("store.index"))
    abort(404)


@store.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = BuyForm()
    store_list = views.website.get_store_list()
    user: web_user.WebUser = current_user
    user.update_info()
    return render_template("store/store.html", store_list=store_list, store_form=form)


def manager_required(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        if not current_user.is_manager():
            abort(403)
        return f(*args, **kwargs)
    return func


@store.route('/check/<string:user>/<string:order>')
@login_required
@manager_required
def check(user, order):
    if not views.website.check_order(order, user):
        abort(404)
    flash(f"订单: {order} 处理成功")
    return redirect(url_for("hello.index"))


def creat_store_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(store, url_prefix="/store")
