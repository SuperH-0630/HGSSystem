from flask import Flask, render_template, Blueprint

import conf
from sql.db import DB
from tool.type_ import Optional, List, Tuple


class RankWebsite:
    main = Blueprint("main", __name__)

    def __init__(self, db: DB):
        self._db = db
        self.app: Flask = Flask(__name__)
        self.app.register_blueprint(self.main)

    def get_rank(self, order_by: str = "DESC") -> Optional[List[Tuple]]:
        cur = self._db.search((f"SELECT UserID, Name, Score, Reputation "
                               f"FROM user "
                               f"WHERE IsManager = 0 "
                               f"ORDER BY Reputation {order_by}, Score {order_by}, UserID {order_by} "
                               f"LIMIT 200;"))

        print(f"SELECT UserID, Name, Score, Reputation "
              f"FROM user "
              f"WHERE IsManager = 0 "
              f"ORDER BY Reputation {order_by}, Score {order_by}, UserID {order_by}"
              f"LIMIT 200;")

        if cur is None:
            return None
        res = []
        for index in range(cur.rowcount):
            i = cur.fetchone()
            res.append((f"NO.{index + 1}", i[1], i[0][:conf.tk_show_uid_len], str(i[3]), str(i[2])))
        return res

    @staticmethod
    @main.route('/')
    def index():
        global website
        return render_template("index.html", loc=conf.base_location)

    @staticmethod
    @main.route('/rank_up')
    def rank_up():
        global website
        head = ["#", "UserName", "UserID", "Reputation", "Score"]
        data = website.get_rank("DESC")
        return render_template("ranking.html", rank_head=head, rank_info=data, ranking_name="高分榜")

    @staticmethod
    @main.route('/rank_down')
    def rank_down():
        global website
        head = ["#", "UserName", "UserID", "Reputation", "Score"]
        data = website.get_rank("ASC")
        return render_template("ranking.html", rank_head=head, rank_info=data, ranking_name="警示榜")

    @staticmethod
    @main.app_errorhandler(404)
    def error_404(e):
        return render_template("error.html", error_code="404", error_info=e), 404

    def run(self):
        self.app.run()


website: Optional[RankWebsite] = None


def creat_ranking_website(db: DB):
    global website
    if website is not None:
        return website, website.app
    website = RankWebsite(db)
    return website, website.app


if __name__ == '__main__':
    mysql_db = DB()
    web, app = creat_ranking_website(mysql_db)
    web.run()
