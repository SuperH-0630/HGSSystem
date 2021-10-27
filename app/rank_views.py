from conf import Config
from flask import render_template, Blueprint, Flask
from .rank_web import RankWebsite
from sql.db import DB
from tool.type_ import Optional

main = Blueprint("main", __name__)
rank_website: Optional[RankWebsite] = None
rank_app: Optional[Flask] = None


@main.route('/')
def index():
    return render_template("index.html", loc=Config.base_location)


@main.route('/rank_up')
def rank_up():
    global rank_website
    head = ["#", "UserName", "UserID", "Reputation", "Score"]
    data = rank_website.get_rank("DESC")
    return render_template("ranking.html", rank_head=head, rank_info=data, ranking_name="高分榜")


@main.route('/rank_down')
def rank_down():
    global rank_website
    head = ["#", "UserName", "UserID", "Reputation", "Score"]
    data = rank_website.get_rank("ASC")
    return render_template("ranking.html", rank_head=head, rank_info=data, ranking_name="警示榜")


@main.app_errorhandler(404)
def error_404(e):
    return render_template("error.html", error_code="404", error_info=e), 404


def creat_ranking_website(db: DB):
    global rank_website, rank_app
    if rank_website is not None:
        return rank_website, rank_website.app
    rank_app = Flask(__name__)
    rank_app.register_blueprint(main)
    rank_website = RankWebsite(db, rank_app)
    return rank_website, rank_app
