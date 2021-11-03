from flask import render_template, Blueprint, Flask, request, abort
from tool.type_ import Optional
from app import views

rank = Blueprint("rank", __name__)
app: Optional[Flask] = None


@rank.route('/up')
def rank_up():
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        abort(404)
    else:
        data = views.website.get_rank(page, "DESC")
        return render_template("rank/ranking.html", rank_info=data, ranking_name="高分榜")


@rank.route('/down')
def rank_down():
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        abort(404)
    else:
        data = views.website.get_rank(page, "ASC")
        return render_template("rank/ranking.html", rank_info=data, ranking_name="警示榜")


def creat_ranking_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(rank, url_prefix="/rank")
