from flask import Flask
from flask_login import current_user
import math

from sql.store import get_store_item_list, get_store_item, confirm_order

from tool.typing import *
from tool.page import get_page

from core.garbage import GarbageType

from sql import DBBit
from sql.db import DB
from sql.garbage import count_garbage_by_uid, get_garbage_by_uid
from sql.user import find_user_by_name, find_user_by_id, get_rank_for_user, count_all_user
from sql.news import write_news, get_news, get_news_count, delete_news
from sql.store import check_order, get_goods_from_order, set_goods_quantity, set_goods_score, add_new_goods

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
        return count_garbage_by_uid(uid, self._db, time_limit=False)

    def get_user_garbage_list(self, uid: uid_t, limit: int, offset: int = 0):
        garbage_list = get_garbage_by_uid(uid,
                                          columns=["UseTime", "Location", "GarbageType", "CheckResult"],
                                          limit=limit,
                                          db=self.db,
                                          offset=offset)
        res = []
        for i in garbage_list:
            t = i[0].strftime("%Y-%m-%d %H:%M:%S")
            loc = i[1]
            type_ = GarbageType.GarbageTypeStrList_ch[int(i[2])]
            if i[3] is None:
                result = "待确定"
                result_class = 'wait'
            elif i[3] == DBBit.BIT_1:
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
        # 更快的写法应该是 web_goods.Goods(*goods), 但目前的写法可读性更佳
        return web_goods.Goods(name=goods[0], score=goods[1], quantity=goods[2], goods_id=goods[3])

    def check_order(self, order, uid) -> Tuple[Optional[list], Optional[str]]:
        if not check_order(order, uid, self._db):
            return None, None
        goods = get_goods_from_order(order, self._db)
        res = []
        for i in goods:
            res.append(f"#{i} {i[0]} x {i[1]}")
        return res, uid

    def confirm_order(self, order_id: int, uid: uid_t) -> bool:
        return confirm_order(order_id, uid, self._db)

    def set_goods_quantity(self, quantity: int, goods_id: int):
        return set_goods_quantity(quantity, goods_id, self._db)

    def set_goods_score(self, score: score_t, goods_id: int):
        return set_goods_score(score, goods_id, self._db)

    def add_new_goods(self, name: str, score: score_t, quantity: int):
        return add_new_goods(name, score, quantity, self._db)


class RankWebsite(WebsiteBase):
    def get_rank(self, page: int, order_by: str = "DESC", url: str = "rank_up"):
        count = math.ceil(count_all_user(self._db) / 20)
        offset = 20 * (page - 1)
        return get_rank_for_user(self.db, 20, offset, order_by), get_page(f"rank.{url}", page, count)


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

    def delete_news(self, context_id: str):
        return delete_news(context_id, self._db)


class DataWebsite(WebsiteBase):
    def count_by_days(self):
        cur = self._db.search(columns=["GarbageType", "DATE_FORMAT(UseTime,'%H') AS days", "count(GarbageID) AS count"],
                              table="garbage",
                              group_by=["GarbageType", "days"],
                              order_by=[("GarbageType", "ASC"), ("days", "ASC")],
                              where="UseTime IS NOT NULL")
        return cur.fetchall()

    def count_by_times(self, days):
        cur = self._db.search(columns=["GarbageType", "days", "count(GarbageID) AS count"],
                              table=f"garbage_{days}d",
                              group_by=["GarbageType", "days"],
                              order_by=[("GarbageType", "ASC"), ("days", "ASC")],
                              where="UseTime IS NOT NULL")
        return cur.fetchall()


class Website(AuthWebsite, StoreWebsite, RankWebsite, NewsWebsite, DataWebsite, WebsiteBase):
    def __init__(self, app: Flask, db: DB):
        super(Website, self).__init__(app, db)
