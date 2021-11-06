from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from conf import Config

from tool.login import create_uid
from tool.typing import *

from core.user import User
from . import views


class WebAnonymous(AnonymousUserMixin):
    """ 网页匿名用户 """
    def __init__(self):
        self.group = "匿名用户"
        self.score = "0"
        self.reputation = "0"
        self.rubbish = "0"
        self.is_manager = lambda: False

    @staticmethod
    def get_qr_code():
        return ""

    @property
    def name(self):
        return ""

    @property
    def uid(self):
        return ""

    @property
    def order(self):
        return ""

    @staticmethod
    def get_order_goods_list():
        return []

    @staticmethod
    def get_garbage_list_count():
        return 0

    @staticmethod
    def get_garbage_list(limit, offset):
        return []

    @staticmethod
    def get_user():
        return None


class WebUser(UserMixin):
    """ 网页用户 """
    def __init__(self, name: uname_t, passwd: passwd_t = None, uid: uid_t = None):
        super(WebUser, self).__init__()
        self._name = name
        if uid is None:
            self._uid = create_uid(name, passwd)
        else:
            self._uid = uid
        self.score = "0"
        self.reputation = "0"
        self.rubbish = "0"
        self.group = "普通成员"
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

    @property
    def is_active(self):
        """Flask要求的属性"""
        return views.website.load_user_by_id(self._uid) is not None

    @property
    def is_authenticated(self):
        """Flask要求的属性"""
        return views.website.load_user_by_id(self._uid) is not None

    def get_id(self):
        """Flask要求的方法"""
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def uid(self):
        return self._uid[:Config.show_uid_len]

    @property
    def order(self) -> str:
        cur = views.website.db.search(columns=["OrderID"],
                                      table="orders",
                                      where=f"UserID = '{self._uid}' and status=0")
        if cur is None or cur.rowcount == 0:
            return "None"
        assert cur.rowcount == 1
        return str(cur.fetchone()[0])

    def is_manager(self):
        return self.group == "管理员"

    def get_qr_code(self):
        s = Serializer(Config.passwd_salt, expires_in=3600)  # 1h有效
        token = s.dumps({"order": f"{self.order}", "uid": f"{self._uid}"})
        return self.order, self._uid, token

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

    def get_garbage_list_count(self):
        return views.website.get_user_garbage_count(self._uid)

    def get_garbage_list(self, limit: int, offset: int = 0):
        return views.website.get_user_garbage_list(self._uid, limit=limit, offset=offset)

    def get_user(self) -> User:
        res = views.website.get_user_by_id(self._uid)
        return res

    def write_news(self, text: str):
        return views.website.write_news(text, self._uid)
