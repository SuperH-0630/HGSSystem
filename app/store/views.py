from flask import render_template, Blueprint, Flask, redirect, url_for, abort, flash
from wtforms import TextField, SubmitField
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_login import login_required

from sql.db import DB

from tool.type_ import Optional
from . import web
from ..auth.web import WebUser

store = Blueprint("store", __name__)
app: Optional[Flask] = None
store_web: Optional[web.StoreWebsite] = None


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
            goods = store_web.get_goods(goods_id)
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
    store_list = store_web.get_store_list()
    user: WebUser = current_user
    user.update_info()
    return render_template("store/store.html", store_list=store_list, store_form=form)


def creat_store_website(app_: Flask, db: DB):
    global store_web, app
    if store_web is None:
        app = app_
        app.register_blueprint(store, url_prefix="/store")
        store_web = web.StoreWebsite(db, app)
