from conf import Config
from flask import render_template, Blueprint, Flask
from tool.type_ import Optional

hello_web = Blueprint("hello_web", __name__)
hello_app: Optional[Flask] = None


@hello_web.route('/')
def index():
    return render_template("hello_web/index.html", loc=Config.base_location)


@hello_web.route('/start')
def start():
    return render_template("hello_web/start.html", loc=Config.base_location)


@hello_web.app_errorhandler(404)
def error_404(e):
    return render_template("hello_web/error.html", error_code="404", error_info=e), 404


def creat_hello_website(app: Flask):
    global hello_app
    if hello_app is not None:
        return hello_app
    app.register_blueprint(hello_web)
