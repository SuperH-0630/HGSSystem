from tool.type_ import *
from enum import Enum


class UserNotSupportError(Exception):
    pass


class UserType(Enum):
    normal: enum = 1
    manager: enum = 2


class User:
    def __init__(self, name: uname_t, uid: uid_t, user_type: enum):
        self._name: uname_t = name
        self._uid: uid_t = uid
        self._type: enum = user_type

    def get_uid(self) -> uid_t:
        return self._uid

    def get_name(self) -> uname_t:
        return self._name

    def get_info(self) -> Dict[str: uid_t, str: uname_t]:
        return {
            "name": self._name,
            "uid": self._uid,
        }

    def evaluate(self) -> score_t:
        raise UserNotSupportError

    def add_score(self, score: score_t) -> score_t:
        raise UserNotSupportError

    def throw_rubbish(self) -> count_t:
        raise UserNotSupportError


class NormalUser(User):
    def __init__(self, name: uname_t, uid: uid_t, reputation: score_t, rubbish: count_t, score: score_t):
        super(NormalUser, self).__init__(name, uid, UserType.normal)
        self._reputation = reputation
        self._rubbish = rubbish
        self._score = score

    def get_info(self) -> Dict[str: uid_t, str: uname_t, str: score_t, str: count_t]:
        """
        获取当前用户的简单信息
        :return: 用户信息字典
        """
        return {
            "name": self._name,
            "uid": self._uid,
            "reputation": self._reputation,
            "rubbish": self._rubbish,
            "score": self._score
        }

    def evaluate(self) -> score_t:
        """
        评估信誉积分
        :return: 信誉积分
        """
        ...

    def add_score(self, score: score_t) -> score_t:
        self._score += score
        return self._score

    def throw_rubbish(self) -> count_t:
        self._rubbish += 1
        return self._rubbish


class ManagerUser(User):
    def __init__(self, name: uname_t, uid: uid_t):
        super(ManagerUser, self).__init__(name, uid, UserType.normal)
