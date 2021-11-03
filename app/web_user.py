from conf import Config

from tool.login import create_uid
from tool.type_ import *

from core.user import User
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
        user = views.website.get_user_by_id(self._uid)
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
        return views.website.load_user_by_id(self._uid) is not None

    @property
    def is_authenticated(self):
        return views.website.load_user_by_id(self._uid) is not None

    @property
    def order(self) -> str:
        cur = views.website.db.search(columns=["OrderID"],
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
        cur = views.website.db.search(columns=["Name", "Quantity"],
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
        return views.website.get_user_garbage_list(self._uid, limit=20)

    def get_user(self) -> User:
        res = views.website.get_user_by_id(self._uid)
        return res
