import conf
import abc
from tool.type_ import *
from sql.db import DB, mysql_db
from sql.user import update_user, find_user_by_id
from sql.garbage import update_garbage
from equipment.scan import HGSCapture, HGSQRCoder, QRCode, capture, qr_capture
from equipment.scan_user import scan_user
from equipment.scan_garbage import scan_garbage
from core.user import User
from core.garbage import GarbageBag, GarbageType, GarbageBagNotUse


class ControlError(Exception):
    ...


class ControlNotLogin(ControlError):
    ...


class ThrowGarbageError(ControlError):
    ...


class CheckGarbageError(ControlError):
    ...


class ControlBase(metaclass=abc.ABCMeta):
    __control = None

    def __new__(cls, *args, **kwargs):
        if cls.__control is None:
            cls.__control = super().__new__()
        return cls.__control

    def __init__(self,
                 db: DB = mysql_db,
                 cap: HGSCapture = capture,
                 qr: HGSQRCoder = qr_capture,
                 loc: location_t = conf.base_location):
        self._db: DB = db
        self._cap = cap
        self._qr = qr
        self._loc: location_t = loc
        self._user: Optional[User] = None  # 操作者

    def scan(self) -> bool:
        """
        处理扫码事务
        二维码扫描的任务包括: 登录, 扔垃圾, 标记垃圾
        :return:
        """
        self._cap.get_image()
        qr_code = self._qr.get_qr_code()

        user: Optional[User] = scan_user(qr_code, self._db)
        if user is not None:
            self.switch_user(user)
            return True

        garbage: Optional[GarbageBag] = scan_garbage(qr_code, self._db)
        if garbage is not None:
            if self._user is None:
                raise ControlNotLogin
            return True

    def throw_garbage(self, garbage: GarbageBag):
        garbage_type = self.get_rubbish_type()  # 获得垃圾类型
        if not self._user.throw_rubbish(garbage, garbage_type, self._loc):
            raise ThrowGarbageError
        update_garbage(garbage, self._db)
        update_user(self._user, self._db)

    def check_garbage(self, garbage: GarbageBag):
        check_result = self.get_rubbish_check()  # 获取垃圾检查结果
        user = find_user_by_id(garbage.get_user(), self._db)
        if user is None:
            raise GarbageBagNotUse
        if not self._user.check_rubbish(garbage, check_result, user):
            raise CheckGarbageError
        update_garbage(garbage, self._db)
        update_user(self._user, self._db)
        update_user(user, self._db)

    @abc.abstractmethod
    def get_rubbish_type(self) -> enum:
        ...

    @abc.abstractmethod
    def get_rubbish_check(self) -> bool:
        ...

    def switch_user(self, user: User) -> bool:
        """
        切换用户: 退出/登录
        :param user: 新用户
        :return: 登录-True, 退出-False
        """
        if self._user is not None and self._user.get_uid() == user.get_uid():
            self._user = None  # 退出登录
            return False
        self._user = user
        return True  # 登录

    def get_user_info(self):
        if self._user is None:
            raise ControlNotLogin
        return self._user.get_info()
