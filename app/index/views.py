from flask import render_template, Blueprint, Flask
from tool.typing import Optional

hello = Blueprint("hello", __name__)
app: Optional[Flask] = None


@hello.route('/')
def start():
    """
    显示 start 宇宙界面
    """
    return render_template("hello/start.html")


@hello.route('/index')
def index():
    """
    显示主页 (介绍页)
    """
    return render_template("hello/index.html")


def creat_hello_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(hello)
