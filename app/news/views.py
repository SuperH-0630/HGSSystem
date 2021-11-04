from flask import render_template, Blueprint, Flask, redirect, url_for, flash, abort, request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_login import login_required, current_user
import functools

from tool.typing import Optional

from app import views
from app.web_user import WebUser

news = Blueprint("news", __name__)
app: Optional[Flask] = None


class WriteForm(FlaskForm):
    """
    写新内容表单
    """
    context = TextAreaField(validators=[DataRequired(message="请输入内容")])
    submit = SubmitField()


class NewDelete(FlaskForm):
    """
    删除内容表单
    """
    submit = SubmitField()


@news.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Get请求时: 显示(获取)新闻消息
    Post请求: 写新闻消息
    :return:
    """
    write_form = WriteForm()
    if write_form.validate_on_submit():
        if len(write_form.context.data) < 20:  # 字数要大于20, 升高发消息的门槛
            flash("请输入20个字符以上的内容")
            return redirect(url_for("news.index", page=1))

        user: WebUser = current_user  # 这一步赋值只是为了添加类型标注, 方便IDE识别
        if not user.write_news(write_form.context.data):
            abort(500)
        return redirect(url_for("news.index", page=1))
    page = int(request.args.get("page", 1))
    res, context_list, page_list = views.website.get_news(page)
    if not res:
        abort(404)
    delete_form = NewDelete()
    return render_template("news/news.html", form=write_form, context_list=context_list,
                           page_list=page_list, page=f"{page}", news_delete=delete_form)


def manager_required(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        if not current_user.is_manager():
            abort(403)
        return f(*args, **kwargs)

    return func


@news.route('/delete', methods=['POST'])
@login_required
@manager_required
def delete():
    context_id = request.args.get("context")
    if context_id is None:
        abort(404)
    if not views.website.delete_news(context_id):
        abort(404)
    flash(f"删除内容 {context_id} 成功")
    return redirect(url_for("news.index"))


def creat_news_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(news, url_prefix="/news")
