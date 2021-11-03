from sql.user import update_user
from sql.store import update_goods, get_order_id, write_goods

from tool.type_ import *
from core.user import User, UserNotSupportError
from . import views
from . import web_user


class Goods:
    def __init__(self, name: str, score: score_t, quantity: int, goods_id: int):
        self._name = name
        self._quantity = quantity
        self._score = score
        self._id = goods_id

    def buy_for_user(self, quantity: int, user_: web_user.WebUser) -> Tuple[int, int]:
        assert quantity > 0
        user: User = user_.get_user()
        if user is None:
            return -4, 0

        score_ = quantity * self._score
        if quantity > self._quantity or quantity <= 0:
            return -2, 0
        try:
            score = user.get_score()
        except UserNotSupportError:
            return -1, 0
        if score < score_:
            return -3, 0

        user.add_score(-score_)
        update_user(user, views.website.db)

        self._quantity -= quantity
        update_goods(self._id, self._quantity, views.website.db)

        order_id = get_order_id(user.get_uid(), views.website.db)
        if order_id is None:
            return -4, 0

        if not write_goods(self._id, quantity, order_id, views.website.db):
            return -4, 0
        return 0, order_id
