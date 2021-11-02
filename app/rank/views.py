from flask import render_template, Blueprint, Flask
from .web import RankWebsite
from sql.db import DB
from tool.type_ import Optional

rank = Blueprint("rank", __name__)
rank_website: Optional[RankWebsite] = None
app: Optional[Flask] = None


@rank.route('/up/<int:page>')
def rank_up(page: int):
    global rank_website
    data = rank_website.get_rank(page, "DESC")
    return render_template("rank/ranking.html", rank_info=data, ranking_name="高分榜")


@rank.route('/down/<int:page>')
def rank_down(page: int):
    global rank_website
    data = rank_website.get_rank(page, "ASC")
    return render_template("rank/ranking.html", rank_info=data, ranking_name="警示榜")


def creat_ranking_website(app_: Flask, db: DB):
    global rank_website, app
    if rank_website is None:
        app = app_
        app.register_blueprint(rank, url_prefix="/rank")
        rank_website = RankWebsite(db, app_)
