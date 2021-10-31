from flask import Flask
from .hello_views import creat_hello_website
from .rank_views import creat_ranking_website

from sql.db import DB


def register(app: Flask, db: DB):
    creat_hello_website(app)
    creat_ranking_website(app, db)
