import math

from flask import render_template, Blueprint, Flask, request, url_for, redirect, flash, abort
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

import base64
import qrcode
from io import BytesIO

from tool.type_ import *
from tool.page import get_page

from app import views
from app import web_user

auth = Blueprint("auth", __name__)
app: Optional[Flask] = None

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


class LoginForm(FlaskForm):
    name = StringField("你的用户名是？", validators=[DataRequired(message="请输入用户名")])
    passwd = PasswordField("用户密码是？", validators=[DataRequired(message="请输入密码")])
    submit = SubmitField("登录")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        passwd = form.passwd.data
        check = views.website.load_user_by_name(name, passwd)

        if check is not None:
            login_user(user=check, remember=True)
            next_page: str = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for("hello.index")
            return redirect(next_page)

        flash("用户错误")
    return render_template("auth/login.html", form=form)


@login_manager.user_loader
def load_user(user: uid_t):
    return views.website.load_user_by_id(user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("用户退出成功")
    return redirect(url_for("hello.index"))


@auth.route("/about")
@login_required
def about():
    user: web_user.WebUser = current_user
    user.update_info()

    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        abort(404)
    else:
        count = math.ceil(current_user.get_garbage_list_count() / 10)
        garbage_list = current_user.get_garbage_list(limit=10, offset=(page - 1) * 10)
        order_list = user.get_order_goods_list()
        return render_template("auth/about.html", order=user.order, order_list=order_list,
                               garbage_list=garbage_list, page_list=get_page("auth.about", page, count), page=page)


@auth.route("/order")
@login_required
def order_qr():
    user: web_user.WebUser = current_user
    user.update_info()

    order, user, token = user.get_qr_code()

    check_image = qrcode.make(data=url_for("store.check", user=user, order=order, _external=True))
    check_img_buffer = BytesIO()
    check_image.save(check_img_buffer, format='JPEG')
    check_qr_data = check_img_buffer.getvalue()
    check_qr_base64 = base64.b64encode(check_qr_data).decode("utf-8")

    confirm_image = qrcode.make(data=url_for("store.confirm", token=token, _external=True))
    confirm_img_buffer = BytesIO()
    confirm_image.save(confirm_img_buffer, format='JPEG')
    confirm_qr_data = confirm_img_buffer.getvalue()
    confirm_qr_base64 = base64.b64encode(confirm_qr_data).decode("utf-8")

    return render_template("auth/qr.html", check_qr_base64=check_qr_base64,
                           confirm_qr_base64=confirm_qr_base64, order=order)


def creat_auth_website(app_: Flask):
    global app
    if app is None:
        app = app_
        login_manager.init_app(app)
        app.register_blueprint(auth, url_prefix="/auth")
        login_manager.anonymous_user = web_user.WebAnonymous
