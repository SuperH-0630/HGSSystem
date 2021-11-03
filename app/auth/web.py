from flask import Flask
import datetime

from conf import Config

from tool.login import create_uid
from tool.type_ import *

from core.user import User
from core.garbage import GarbageType

from sql import DBBit
from sql.db import DB
from sql.user import find_user_by_name, find_user_by_id
from . import views


class WebUser:
    def __init__(self, name: uname_t, passwd: passwd_t = None, uid: uid_t = None):
        self._name = name
        if uid is None:
            self._uid = create_uid(name, passwd)
        else:
            self._uid = uid
        self.score = "0"
        self.reputation = "0"
        self.rubbish = "0"
        self.group = "普通成员"
        self.is_anonymous = False
        self.update_info()

    def update_info(self):
        user = views.auth_website.get_user_by_id(self._uid)
        if user is None:
            return
        if user.is_manager():
            self.group = "管理员"
            self.score = "0"
            self.reputation = "0"
            self.rubbish = "0"
        else:
            self.group = "普通成员"
            res = user.get_info()
            self.score = res.get('score', '0')
            self.reputation = res.get('reputation', '0')
            self.rubbish = res.get('rubbish', '0')

    def is_manager(self):
        return self.group == "管理员"

    def get_qr_code(self):
        return self.order, self._uid

    @property
    def name(self):
        return self._name

    @property
    def uid(self):
        return self._uid[:Config.tk_show_uid_len]

    @property
    def is_active(self):
        return views.auth_website.load_user_by_id(self._uid) is not None

    @property
    def is_authenticated(self):
        return views.auth_website.load_user_by_id(self._uid) is not None

    @property
    def order(self) -> str:
        cur = views.auth_website.db.search(columns=["OrderID"],
                                           table="orders",
                                           where=f"UserID = '{self._uid}' and status=0")
        if cur is None or cur.rowcount == 0:
            return "None"
        assert cur.rowcount == 1
        return str(cur.fetchone()[0])

    def get_order_goods_list(self):
        order = self.order
        if order is None:
            return []
        cur = views.auth_website.db.search(columns=["Name", "Quantity"],
                                           table="order_goods_view",
                                           where=f"OrderID = '{order}'")
        if cur is None:
            return []

        res = []
        for i in range(cur.rowcount):
            re = cur.fetchone()
            res.append(f"#{i} {re[0]} x {re[1]}")
        return res

    def get_id(self):
        return self._uid

    def get_garbage_list(self):
        return views.auth_website.get_user_garbage_list(self._uid, limit=20)

    def get_user(self) -> User:
        res = views.auth_website.get_user_by_id(self._uid)
        return res


class AuthWebsite:
    def __init__(self, app: Flask, db: DB):
        self._app = app
        self._db = db

    @property
    def db(self):
        return self._db

    def load_user_by_name(self, name: uname_t, passwd: passwd_t) -> Optional[WebUser]:
        user = find_user_by_name(name, passwd, self._db)
        if user is None:
            return None
        return WebUser(name, uid=user.get_uid())

    def load_user_by_id(self, uid: uid_t) -> Optional[WebUser]:
        user = find_user_by_id(uid, self._db)
        if user is None:
            return None
        name = user.get_name()
        return WebUser(name, uid=uid)

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
