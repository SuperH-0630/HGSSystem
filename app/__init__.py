from flask import Flask

from tool.type_ import *
from sql.db import DB

from . import views as views

app: Optional[Flask] = None


def creat_web(db: DB) -> Flask:
    global app
    if app is not None:
        return app
    app = Flask(__name__)
    views.register(app, db)
    return app
