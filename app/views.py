from flask import Flask
from app.index.views import creat_hello_website
from app.rank.views import creat_ranking_website
from app.auth.views import creat_auth_website

from sql.db import DB


def register(app: Flask, db: DB):
    creat_hello_website(app)
    creat_ranking_website(app, db)
    creat_auth_website(app, db)
