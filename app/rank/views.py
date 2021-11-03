from flask import render_template, Blueprint, Flask
from tool.type_ import Optional
from app import views

rank = Blueprint("rank", __name__)
app: Optional[Flask] = None


@rank.route('/up/<int:page>')
def rank_up(page: int):
    data = views.website.get_rank(page, "DESC")
    return render_template("rank/ranking.html", rank_info=data, ranking_name="高分榜")


@rank.route('/down/<int:page>')
def rank_down(page: int):
    data = views.website.get_rank(page, "ASC")
    return render_template("rank/ranking.html", rank_info=data, ranking_name="警示榜")


def creat_ranking_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(rank, url_prefix="/rank")
