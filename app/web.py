from sql.store import get_store_item_list, get_store_item, check_order

from flask import Flask
import datetime

from conf import Config

from tool.type_ import *

from core.garbage import GarbageType

from sql import DBBit
from sql.db import DB
from sql.user import find_user_by_name, find_user_by_id

from . import web_user
from . import web_goods


class WebsiteBase:
    def __init__(self, app: Flask, db: DB):
        self._db = db
        self._app = app


class AuthWebsite(WebsiteBase):
    @property
    def db(self):
        return self._db

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

    def get_user_garbage_list(self, uid: uid_t, limit: int):
        cur = self._db.search(columns=["UseTime", "Location", "GarbageType", "CheckResult"],
                              table="garbage",
                              where=f"UserID='{uid}'",
                              limit=limit)
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
    @property
    def db(self):
        return self._db

    def get_store_list(self) -> Optional[List]:
        return get_store_item_list(self._db)

    def get_goods(self, goods_id: int):
        goods = get_store_item(goods_id, self._db)  # 返回值 ["Name", "Score", "Quantity", "GoodsID"]
        if goods is None:
            return goods
        return web_goods.Goods(*goods)

    def check_order(self, order_id: int, uid: uid_t) -> bool:
        return check_order(order_id, uid, self._db)


class RankWebsite(WebsiteBase):
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


class Website(AuthWebsite, StoreWebsite, RankWebsite, WebsiteBase):
    def __init__(self, app: Flask, db: DB):
        super(Website, self).__init__(app, db)
