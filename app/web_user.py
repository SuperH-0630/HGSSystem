from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from conf import Config

from tool.typing import *

from sql import DBBit
from sql.user import search_from_user_view
from sql.garbage import count_garbage_by_uid

from core.user import User, UserType
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
    """
    网页用户
    代表一个网页端的登录
    网页端只有在积分商城兑换礼品时会对数据加锁
    """

    def __init__(self, name: uname_t, uid: uid_t):
        self._uid = uid
        self._name = name
        self._score = 0
        self._reputation = 0
        self._type = UserType.normal
        self._rubbish = 0

        super(WebUser, self).__init__()
        self.update_info()

    def update_info(self) -> bool:
        info = search_from_user_view(columns=["Score", "Reputation", "IsManager"],
                                     where=f"UserID='{self._uid}'",
                                     db=views.website.db)
        if info is None:
            return False
        info = info[0]
        self._score = int(info[0])
        self._reputation = int(info[1])
        self._type = UserType.manager if info[2] == DBBit.BIT_1 else UserType.normal
        self._rubbish = count_garbage_by_uid(self.uid, views.website.db)
        if self._rubbish == -1:
            return False
        return True

    @property
    def score(self):
        return f"{self._score}"

    @property
    def reputation(self):
        return f"{self._reputation}"

    @property
    def rubbish(self):
        return f"{self._rubbish}"

    @property
    def group(self):
        return "管理员" if self._type == UserType.manager else "普通成员"

    def is_manager(self):
        return self._type == UserType.manager

    @property
    def is_active(self):
        """Flask要求的属性, 表示用户是否激活(可登录), HGSSystem没有封禁用户系统, 所有用户都是被激活的"""
        return True

    @property
    def is_authenticated(self):
        """Flask要求的属性, 表示登录的凭据是否正确, 这里检查是否能 load_user_by_id"""
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

    def get_order_qr_code(self):
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
        return views.website.get_user_by_id(self._uid)

    def write_news(self, text: str):
        return views.website.write_news(text, self._uid)
