import datetime

from sql.db import DB
from tool.type_ import *
from tool.string import mysql_str


def write_news(text, uid: uid_t, db: DB):
    text = mysql_str(text)
    cur = db.insert(table="context",
                    columns=["Context", "Author"],
                    values=f"'{text}', '{uid}'")
    if cur is None:
        return False
    assert cur.rowcount == 1
    return True


def get_news(db: DB, limit: Optional[int] = None, offset: Optional[int] = None):
    cur = db.search(columns=["ContextID", "Context", "Name", "Time"],
                    table="context_user",
                    limit=limit,
                    offset=offset,
                    order_by=[("Time", "DESC")])
    if cur is None:
        return False, None
    res = []
    for i in range(cur.rowcount):
        re = cur.fetchone()
        time: datetime.datetime = re[3]
        res.append((re[0], re[1], re[2], time.strftime("%Y-%m-%d %H:%M")))
    return True, res


def get_news_count(db: DB):
    cur = db.search(columns=["count(ContextID)"], table="context_user")
    if cur is None:
        return 0
    assert cur.rowcount == 1
    return int(cur.fetchone()[0])
