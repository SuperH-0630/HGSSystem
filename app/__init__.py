from flask import Flask
from waitress import serve

from conf import Config
from tool.type_ import *
from sql.db import DB

from . import views as views

app: Optional["App"] = None


class App:
    app: Optional["App"] = None

    def __new__(cls, *args, **kwargs):
        if App.app is not None:
            return App.app
        return object.__new__(cls)

    def __init__(self):
        self._app = Flask(__name__)

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
