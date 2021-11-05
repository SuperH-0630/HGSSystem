from flask import Flask
from app.index.views import creat_hello_website
from app.rank.views import creat_ranking_website
from app.auth.views import creat_auth_website
from app.store.views import creat_store_website
from app.news.views import creat_news_website
from app.data.views import creat_data_website

from tool.typing import *
from sql.db import DB
from . import web

website: "Optional[web.Website]" = None


def register(app: Flask, db: DB):
    """
    注册蓝板, 并定义一些内容
    """
    global website
    if website is None:
        website = web.Website(app, db)

    creat_hello_website(app)
    creat_ranking_website(app)
    creat_auth_website(app)
    creat_store_website(app)
    creat_news_website(app)
    creat_data_website(app)
