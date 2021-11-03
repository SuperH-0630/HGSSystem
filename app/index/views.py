from flask import render_template, Blueprint, Flask
from tool.type_ import Optional

hello = Blueprint("hello", __name__)
app: Optional[Flask] = None


@hello.route('/')
def start():
    return render_template("hello/start.html")


@hello.route('/index')
def index():
    return render_template("hello/index.html")


@hello.app_errorhandler(404)
def error_404(e):
    return render_template("hello/error.html", error_code="404", error_info=e), 404


@hello.app_errorhandler(403)
def error_403(e):
    return render_template("hello/error.html", error_code="403", error_info=e), 403


def creat_hello_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(hello)
