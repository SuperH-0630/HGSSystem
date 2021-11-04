from flask import Flask
from flask_login import current_user
import datetime
import math

from conf import Config

from sql.store import get_store_item_list, get_store_item, confirm_order

from tool.type_ import *
from tool.page import get_page

from core.garbage import GarbageType

from sql import DBBit
from sql.db import DB
from sql.user import find_user_by_name, find_user_by_id
from sql.news import write_news, get_news, get_news_count

from . import web_user
from . import web_goods


class WebsiteBase:
    def __init__(self, app: Flask, db: DB):
        self._db = db
        self._app = app
        self._user = current_user  # 把参函传递的user移迁为该变量

    @property
    def db(self):
        return self._db

    @property
    def app(self):
        return self._app

    @property
    def user(self):
        return self._user

    @property
    def rel_user(self):
        return self._user._get_current_object()


class AuthWebsite(WebsiteBase):
    def load_user_by_name(self, name: uname_t, passwd: passwd_t) -> Optional["web_user.WebUser"]:
        user = find_user_by_name(name, passwd, self._db)
        if user is None:
            return None
        return web_user.WebUser(name, uid=user.get_uid())

    def load_user_by_id(self, uid: uid_t) -> Optional["web_user.WebUser"]:
        user = find_user_by_id(uid, self._db)
        if user is None:
            return None
        name = user.get_name()
        return web_user.WebUser(name, uid=uid)

    def get_user_garbage_count(self, uid: uid_t):
        cur = self._db.search(columns=["count(GarbageID)"],
                              table="garbage",
                              where=f"UserID='{uid}'")
        if cur is None:
            return 0
        assert cur.rowcount == 1
        return int(cur.fetchone()[0])

    def get_user_garbage_list(self, uid: uid_t, limit: int, offset: int = 0):
        cur = self._db.search(columns=["UseTime", "Location", "GarbageType", "CheckResult"],
                              table="garbage",
                              where=f"UserID='{uid}'",
                              limit=limit,
                              offset=offset,
                              order_by=[("UseTime", "DESC")])
        if cur is None or cur.rowcount == 0:
            return None
        res = []
        for i in range(cur.rowcount):
            re: Tuple[datetime.datetime, str, bytes, Optional[bytes]] = cur.fetchone()
            t = re[0].strftime("%Y-%m-%d %H:%M:%S")
            loc = re[1]
            type_ = GarbageType.GarbageTypeStrList_ch[int(re[2])]
            if re[3] is None:
                result = "待确定"
                result_class = 'wait'
            elif re[3] == DBBit.BIT_1:
                result = "投放正确"
                result_class = 'pass'
            else:
                result = "投放错误"
                result_class = 'fail'
            res.append((t, loc, type_, result, result_class))
        return res

    def get_user_by_id(self, uid: uid_t):
        res = find_user_by_id(uid, self._db)
        return res


class StoreWebsite(WebsiteBase):
    def get_store_list(self) -> Optional[List]:
        return get_store_item_list(self._db)

    def get_goods(self, goods_id: int):
        goods = get_store_item(goods_id, self._db)  # 返回值 ["Name", "Score", "Quantity", "GoodsID"]
        if goods is None:
            return goods
        return web_goods.Goods(*goods)

    def check_order(self, order, uid) -> Tuple[Optional[list], Optional[str]]:
        cur = self._db.search(columns=["UserID"],
                              table="orders",
                              where=[f"OrderID='{order}'", f"UserID='{uid}'"])
        if cur is None or cur.rowcount != 1:
            return None, None
        uid = cur.fetchone()[0]

        cur = self._db.search(columns=["Name", "Quantity"],
                              table="order_goods_view",
                              where=f"OrderID = '{order}'")
        if cur is None:
            return None, None

        res = []
        for i in range(cur.rowcount):
            re = cur.fetchone()
            res.append(f"#{i} {re[0]} x {re[1]}")
        return res, uid

    def confirm_order(self, order_id: int, uid: uid_t) -> bool:
        return confirm_order(order_id, uid, self._db)


class RankWebsite(WebsiteBase):
    def get_rank(self, page: int, order_by: str = "DESC", url: str = "rank_up"):
        cur = self._db.search(columns=['count(UserID)'], table='user')
        if cur is None:
            return None, None
        assert cur.rowcount == 1
        count = math.ceil(int(cur.fetchone()[0]) / 20)

        offset = 20 * (page - 1)
        cur = self._db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                              table='user',
                              where='IsManager=0',
                              order_by=[('Reputation', order_by), ('Score', order_by), ('UserID', order_by)],
                              limit=20,
                              offset=offset)  # TODO 封装该函数
        if cur is None:
            return None, None
        res = []
        for index in range(cur.rowcount):
            i = cur.fetchone()
            res.append((f"{offset + index + 1}", i[1], i[0][:Config.show_uid_len], str(i[3]), str(i[2])))
        return res, get_page(f"rank.{url}", page, count)


class NewsWebsite(WebsiteBase):
    def write_news(self, context: str, uid: uid_t):
        return write_news(context, uid, self.db)

    def get_news(self, page: int = 1):
        count = math.ceil(get_news_count(self.db) / 10)
        if page > count:
            return False, None, None

        res, news_list = get_news(limit=20, offset=((page - 1) * 10), db=self.db)
        if not res:
            return False, None, None

        return True, news_list, get_page("news.index", page, count)


class Website(AuthWebsite, StoreWebsite, RankWebsite, NewsWebsite, WebsiteBase):
    def __init__(self, app: Flask, db: DB):
        super(Website, self).__init__(app, db)
