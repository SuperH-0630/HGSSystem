from flask import Flask

from conf import Config
from sql.db import DB
from tool.type_ import Optional, List, Tuple


class RankWebsite:
    def __init__(self, db: DB, app: Flask):
        self._db = db
        self.app = app

    @property
    def db(self):
        return self._db

    def get_rank(self, page: int, order_by: str = "DESC") -> Optional[List[Tuple]]:
        offset = 20 * (page - 1)
        cur = self._db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                              table='user',
                              where='IsManager=0',
                              order_by=[('Reputation', order_by), ('Score', order_by), ('UserID', order_by)],
                              limit=20,
                              offset=offset)
        if cur is None:
            return None
        res = []
        for index in range(cur.rowcount):
            i = cur.fetchone()
            res.append((f"{offset + index + 1}", i[1], i[0][:Config.tk_show_uid_len], str(i[3]), str(i[2])))
        return res
