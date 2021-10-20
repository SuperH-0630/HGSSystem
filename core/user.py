import abc
import conf
from tool.type_ import *
from tool.time_ import HGSTime
from .garbage import GarbageBag, GarbageType


class UserException(Exception):
    pass


class UserNotSupportError(UserException):
    pass


class UserNotScoreException(UserException):
    pass


class UserRubbishException(UserException):
    pass


class UserType:
    UserTypeStrList: List = ["", "NORMAL", "MANAGER"]
    normal: enum = 1
    manager: enum = 2


class User(metaclass=abc.ABCMeta):
    def __init__(self, name: uname_t, uid: uid_t, user_type: enum):
        self._name: uname_t = name
        self._uid: uid_t = uid
        self._type: enum = user_type

    def is_manager(self):
        return self._type == UserType.manager

    def get_uid(self) -> uid_t:
        return self._uid

    def get_name(self) -> uname_t:
        return self._name

    def get_user_type(self) -> enum:
        return self._type

    def get_info(self) -> Dict[str, str]:
        raise UserNotSupportError

    def __repr__(self):
        tmp = UserType.UserTypeStrList
        return f"User {self._uid} {self._name} is {tmp[self._type]}"

    def evaluate(self, is_right: bool) -> score_t:
        raise UserNotSupportError

    def add_score(self, score: score_t) -> score_t:
        raise UserNotSupportError

    def throw_rubbish(self, garbage: GarbageBag, garbage_type: enum, loc: location_t) -> bool:
        raise UserNotSupportError

    def check_rubbish(self, garbage: GarbageBag, right: bool, user) -> bool:
        raise UserNotSupportError


class NormalUser(User):
    def __init__(self, name: uname_t, uid: uid_t, reputation: score_t, rubbish: count_t, score: score_t):
        super(NormalUser, self).__init__(name, uid, UserType.normal)
        self._reputation = reputation
        self._rubbish = rubbish
        self._score = score

    def __repr__(self):
        return (f"User {self._uid} {self._name} "
                f"reputation {self._reputation} "
                f"rubbish {self._rubbish} "
                f"score {self._score} "
                f"is NORMAL")

    def get_info(self) -> Dict[str, str]:
        """
        获取当前用户的简单信息
        :return: 用户信息字典
        """
        return {
            "name": str(self._name),
            "uid": str(self._uid),
            "manager": '0',
            "reputation": str(self._reputation),
            "rubbish": str(self._rubbish),
            "score": str(self._score)
        }

    def evaluate(self, is_right: bool) -> score_t:
        """
        评估信誉积分
        使用朴素贝叶斯公式为基础
        总分值: 1000分
        实际分: P(A|B) * 1000
        A=能正确仍对垃圾的概率
        B=本次仍对垃圾的概率

        初始概率:
          P(A) = 0.3  (default_reputation = 300)
          P(B|A) = 0.6
          P(B|^A) = 0.3
          P(B) = 0.8 * 0.3 + 0.1 * 0.7 = 0.31
          p(^B) = 0.69

          P(A|B) = P(A) * (P(B|A) / P(B)) = P(A) * 2.5806
          P(A|^B) = P(A) * (P(^B|A) / P(^B)) = P(A) * (0.2/0.96) = P(A) * 0.2083
        :return: 信誉积分
        """

        if is_right and self._rubbish > conf.max_rubbish_week:
            return self._reputation

        pa = self._reputation / 1000  # P(A)
        if pa < 0.01:
            pa = 0.01
        p_a = 1 - pa  # P(^A)
        pba, p_ba, pb_a, p_b_a = 0.6, 0.4, 0.3, 0.7  # P(B|A), P(^B|A), P(B|^A), P(^B|^A)
        pb = pba * pa + pb_a * p_a  # P(B) = P(B|A) * P(A) + P(B|^A) * P(^A)
        p_b = p_ba * pa + p_b_a * p_a  # P(^B) = P(^B|A) * P(A) + P(^B|^A) * P(^A)

        if is_right:
            new_pa = pa * (pba / pb)  # P(A|B)
        else:
            new_pa = pa * (p_ba / p_b)  # P(A|^B)
        new_pa = new_pa * 1000
        if int(new_pa) == 0:
            new_pa = 1
        if int(new_pa) > 1000:
            new_pa = 999

        amplitude = new_pa - self._reputation  # 分差
        amplitude_top = 1000 - self._reputation  # 距离总分分差

        if is_right:
            if amplitude >= 20:
                amplitude = amplitude * (amplitude_top / 1000)  # 涨分抑制
        else:
            if amplitude <= -20:
                amplitude = amplitude * (self._reputation / 1000)  # 总分分差月小扣分越高

        self._reputation += int(amplitude)
        if self._reputation <= 5:
            self._reputation = 5
        return self._reputation

    def add_score(self, score: score_t) -> score_t:
        if self._score + score < 0:
            self._score = 0
            raise UserNotScoreException

        self._score += score
        return self._score

    def throw_rubbish(self, garbage: GarbageBag, garbage_type: enum, loc: location_t = conf.base_location) -> bool:
        if self._rubbish > conf.max_rubbish_week:
            try:
                self.add_score(-3)
            except UserNotScoreException:
                raise UserRubbishException
        elif self._rubbish > conf.limit_rubbish_week:
            raise UserRubbishException

        if garbage.is_use() or garbage.is_check()[0]:
            return False
        garbage.config_use(garbage_type, HGSTime(), self._uid, loc)

        self._rubbish += 1
        return True

    def check_rubbish(self, garbage: GarbageBag, right: bool, user: User) -> bool:
        raise UserNotSupportError


class ManagerUser(User):
    def __init__(self, name: uname_t, uid: uid_t):
        super(ManagerUser, self).__init__(name, uid, UserType.manager)

    def check_rubbish(self, garbage: GarbageBag, right: bool, user: User) -> bool:
        if (not garbage.is_use()) or garbage.is_check()[0] or user.get_uid() != garbage.get_user():
            return False

        garbage.config_check(right, self._uid)
        user.evaluate(right)

        try:
            if right:
                if garbage.get_type() == GarbageType.recyclable:
                    user.add_score(3)
                elif garbage.get_type() == GarbageType.kitchen or garbage.get_type() == GarbageType.hazardous:
                    user.add_score(2)
                else:
                    user.add_score(1)
            else:
                user.add_score(-4)
        except UserNotScoreException:
            ...

        return True

    def get_info(self) -> Dict[str, str]:
        return {
            "name": str(self._name),
            "uid": str(self._uid),
            "manager": '1'
        }
