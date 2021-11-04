from flask import Flask, Blueprint, get_flashed_messages, render_template
from waitress import serve

from conf import Config
from tool.type_ import *
from sql.db import DB

from . import views as views

app: Optional["App"] = None


class App:
    app: Optional["App"] = None
    base = Blueprint("base", __name__)

    @staticmethod
    @base.app_context_processor
    def inject_base():
        return {"loc": Config.base_location,
                "copy_right": "SuperHuan",
                "github_link": r"https://github.com/SuperH-0630/HGSSystem"}

    @staticmethod
    @base.app_context_processor
    def inject_flash_message():
        msg = []
        for i in get_flashed_messages():
            msg.append(i)
        return {"flash_msg": msg,
                "flash_height": len(msg)}

    @staticmethod
    @base.app_errorhandler(404)
    def error_404(e):
        return render_template("error.html", error_code="404", error_info=e), 404

    @staticmethod
    @base.app_errorhandler(403)
    def error_403(e):
        return render_template("error.html", error_code="403", error_info=e), 403

    @staticmethod
    @base.app_errorhandler(500)
    def error_500(e):
        return render_template("error.html", error_code="500", error_info=e), 500

    def __new__(cls, *args, **kwargs):
        if App.app is not None:
            return App.app
        return object.__new__(cls)

    def __init__(self):
        self._app = Flask(__name__)
        self._app.register_blueprint(self.base)

    def conf(self, db: DB):
        self._app.config["SECRET_KEY"] = Config.wtf_secret  # FlaskForm 需要使用
        views.register(self._app, db)

    def run_waitress(self, **kw):
        serve(self._app, **kw)

    def run_flask(self,
                  host: Optional[str] = None,
                  port: Optional[int] = None,
                  debug: Optional[bool] = True if Config.run_type == "debug" else None,
                  load_dotenv: bool = True,
                  **options: any):
        self._app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

    def get_app(self):
        return self._app


def creat_web(db: DB) -> App:
    global app
    if app is not None:
        return app
    app = App()
    app.conf(db)
    return app
