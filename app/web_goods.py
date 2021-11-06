from sql.user import update_user
from sql.store import update_goods, get_order_id, write_goods

from tool.typing import *
from core.user import User, UserNotSupportError
from . import views
from . import web_user


class Goods:
    """ 商品 """
    def __init__(self, name: str, score: score_t, quantity: int, goods_id: int):
        self._name = name
        self._quantity = quantity
        self._score = score
        self._id = goods_id

    def buy_for_user(self, quantity: int, user_: web_user.WebUser) -> Tuple[int, int]:
        """ 兑换商品 """
        score_ = quantity * self._score
        if quantity > self._quantity or quantity <= 0:
            return -2, 0  # 数量错误

        user: User = user_.get_user()
        if user is None:
            return -4, 0  # 系统错误

        try:
            score = user.get_score()
        except UserNotSupportError:
            return -1, 0  # 用户不支持购买

        if score < score_:
            return -3, 0  # 积分不足

        user.add_score(-score_)
        update_user(user, views.website.db)

        self._quantity -= quantity
        update_goods(self._id, self._quantity, views.website.db)

        order_id = get_order_id(user.get_uid(), views.website.db)
        if order_id is None:
            return -4, 0  # 系统错误

        if not write_goods(self._id, quantity, order_id, views.website.db):
            return -4, 0  # 系统错误
        return 0, order_id
