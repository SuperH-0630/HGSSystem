from flask import Flask

import conf
from sql.db import DB
from tool.type_ import Optional, List, Tuple


class RankWebsite:
    def __init__(self, db: DB, app: Flask):
        self._db = db
        self.app = app

    def get_rank(self, order_by: str = "DESC") -> Optional[List[Tuple]]:
        cur = self._db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                              table='user',
                              where='IsManager=0',
                              order_by=[('Reputation', order_by), ('Score', order_by), ('UserID', order_by)],
                              limit=200)
        if cur is None:
            return None
        res = []
        for index in range(cur.rowcount):
            i = cur.fetchone()
            res.append((f"NO.{index + 1}", i[1], i[0][:conf.tk_show_uid_len], str(i[3]), str(i[2])))
        return res

    def run(self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            debug: Optional[bool] = None,
            load_dotenv: bool = True,
            **options,
            ):
        self.app.run(host, port, debug, load_dotenv, **options)
