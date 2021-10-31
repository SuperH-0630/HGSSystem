from conf import Config
from flask import render_template, Blueprint, Flask
from .rank_web import RankWebsite
from sql.db import DB
from tool.type_ import Optional

rank_web = Blueprint("rank_web", __name__)
rank_website: Optional[RankWebsite] = None
rank_app: Optional[Flask] = None


@rank_web.route('/up')
def rank_up():
    global rank_website
    data = rank_website.get_rank("DESC")
    return render_template("rank_web/ranking.html", rank_info=data, ranking_name="高分榜")


@rank_web.route('/down')
def rank_down():
    global rank_website
    data = rank_website.get_rank("ASC")
    return render_template("rank_web/ranking.html", rank_info=data, ranking_name="警示榜")


def creat_ranking_website(app: Flask, db: DB):
    global rank_website, rank_app
    if rank_website is not None:
        return rank_website
    rank_app = app
    rank_app.register_blueprint(rank_web, url_prefix="/rank")
    rank_website = RankWebsite(db, rank_app)
    return rank_website
