from flask import render_template, Blueprint, Flask, request, url_for, redirect, flash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

import base64
import qrcode
from io import BytesIO

from tool.type_ import *
from sql.db import DB
from .web import AuthWebsite, WebUser

auth = Blueprint("auth", __name__)
auth_website: Optional[AuthWebsite] = None
app: Optional[Flask] = None

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


class LoginForm(FlaskForm):
    name = StringField("你的用户名是？", validators=[DataRequired()])
    passwd = PasswordField("用户密码是？", validators=[DataRequired()])
    submit = SubmitField("登录")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        passwd = form.passwd.data
        check = auth_website.load_user_by_name(name, passwd)

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
    return auth_website.load_user_by_id(user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("用户退出成功")
    return redirect(url_for("hello.index"))


@auth.route("/about")
@login_required
def about():
    user: WebUser = current_user
    user.update_info()
    return render_template("auth/about.html", order=user.order, order_list=user.get_order_goods_list())


@auth.route("/order")
@login_required
def order_qr():
    user: WebUser = current_user
    user.update_info()
    order, user = user.get_qr_code()
    image = qrcode.make(data=url_for("store.check", user=user, order=order, _external=True))
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return render_template("auth/qr.html", qr_base64=base64_str, order=order)


def creat_auth_website(app_: Flask, db: DB):
    global auth_website, app
    if auth_website is None:
        app = app_
        auth_website = AuthWebsite(app, db)
        login_manager.init_app(app)
        app.register_blueprint(auth, url_prefix="/auth")
