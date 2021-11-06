from flask import render_template, Blueprint, Flask, request, abort
from tool.typing import Optional
from app import views

rank = Blueprint("rank", __name__)
app: Optional[Flask] = None


@rank.route('/up')
def rank_up():
    """
    高分榜 正向排行
    """
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        abort(404)
    else:
        data, page_list = views.website.get_rank(page, "DESC", "rank_up")
        return render_template("rank/ranking.html", rank_info=data, ranking_name="高分榜",
                               page_list=page_list, page=page)


@rank.route('/down')
def rank_down():
    """
    警示榜 反向排行
    """
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        abort(404)
    else:
        data, page_list = views.website.get_rank(page, "ASC", "rank_down")
        return render_template("rank/ranking.html", rank_info=data, ranking_name="警示榜",
                               page_list=page_list, page=f"{page}")


def creat_ranking_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(rank, url_prefix="/rank")
