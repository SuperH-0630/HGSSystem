from flask import render_template, Blueprint, Flask, redirect, url_for, flash, abort, request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_login import login_required, current_user

from tool.type_ import Optional

from app import views
from app.web_user import WebUser

news = Blueprint("news", __name__)
app: Optional[Flask] = None


class WriteForm(FlaskForm):
    context = TextAreaField(validators=[DataRequired(message="请输入内容")])
    submit = SubmitField()


@news.route('/', methods=['GET', 'POST'])
@login_required
def index():
    write_form = WriteForm()
    if write_form.validate_on_submit():
        if len(write_form.context.data) < 20:
            flash("请输入20个字符以上的内容")
            return redirect(url_for("news.index", page=1))
        user: WebUser = current_user
        if not user.write_news(write_form.context.data):
            abort(500)
        return redirect(url_for("news.index", page=1))
    page = int(request.args.get("page", 1))
    res, context_list, page_list = views.website.get_news(page)
    if not res:
        abort(404)
    return render_template("news/news.html", form=write_form, context_list=context_list,
                           page_list=page_list, page=f"{page}")


def creat_news_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(news, url_prefix="/news")
