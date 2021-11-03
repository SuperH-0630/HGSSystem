from flask import Flask

from sql.db import DB
from sql.user import update_user
from sql.store import get_store_item_list, get_store_item, update_goods, get_order_id, write_goods, check_order
from tool.type_ import *

from core.user import User, UserNotSupportError

from . import views
from ..auth import web as auth_web
from ..auth import views as auth_views


class Goods:
    def __init__(self, name: str, score: score_t, quantity: int, goods_id: int):
        self._name = name
        self._quantity = quantity
        self._score = score
        self._id = goods_id

    def buy_for_user(self, quantity: int, web_user: auth_web.WebUser) -> Tuple[int, int]:
        assert quantity > 0
        user: User = web_user.get_user()
        if user is None:
            return -4, 0

        score_ = quantity * self._score
        if quantity > self._quantity or quantity == 0:
            return -2, 0
        try:
            score = user.get_score()
        except UserNotSupportError:
            return -1, 0
        if score < score_:
            return -3, 0

        user.add_score(-score_)
        update_user(user, auth_views.auth_website.db)

        self._quantity -= quantity
        update_goods(self._id, self._quantity, views.store_web.db)

        order_id = get_order_id(user.get_uid(), views.store_web.db)
        if order_id is None:
            return -4, 0

        if not write_goods(self._id, quantity, order_id, views.store_web.db):
            return -4, 0
        return 0, order_id


class StoreWebsite:
    def __init__(self, db: DB, app: Flask):
        self._db = db
        self.app = app

    @property
    def db(self):
        return self._db

    def get_store_list(self) -> Optional[List]:
        return get_store_item_list(self._db)

    def get_goods(self, goods_id: int):
        goods = get_store_item(goods_id, self._db)  # 返回值 ["Name", "Score", "Quantity", "GoodsID"]
        if goods is None:
            return goods
        return Goods(*goods)

    def check_order(self, order_id: int, uid: uid_t) -> bool:
        return check_order(order_id, uid, self._db)
