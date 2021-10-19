import conf
import time
from tool.type_ import *
from sql.db import DB, mysql_db
from sql.user import update_user, find_user_by_id, creat_new_user
from sql.garbage import update_garbage, creat_new_garbage
from equipment.scan import HGSCapture, HGSQRCoder, QRCode, capture, qr_capture
from equipment.scan_user import scan_user
from equipment.scan_garbage import scan_garbage, write_gid_qr
from core.user import User, UserNotSupportError
from core.garbage import GarbageBag, GarbageType, GarbageBagNotUse


class ControlError(Exception):
    ...


class ControlNotLogin(ControlError):
    ...


class ThrowGarbageError(ControlError):
    ...


class CheckGarbageError(ControlError):
    ...


class CreatGarbageError(ControlError):
    ...


class CreatUserError(ControlError):
    ...


class ControlScanType:
    switch_user = 1
    throw_garbage = 2
    check_garbage = 3
    no_to_done = 4


class Control:
    __control = None

    def __new__(cls, *args, **kwargs):
        if cls.__control is None:
            cls.__control = super(Control, cls).__new__(cls, *args, **kwargs)
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
        self._user_last_time: time_t = 0

    def is_manager(self):
        if not self.check_user():
            return False
        return self._user.is_manager()

    def check_user(self):
        if self._user is None:
            return False
        if not self._user.is_manager() and time.time() - self._user_last_time > 20:
            self._user = None
            return False
        return True

    def __check_user(self):
        if not self.check_user():
            raise ControlNotLogin
        self._user_last_time = time.time()

    def __check_normal_user(self):
        self.__check_user()
        if self._user.is_manager():
            raise UserNotSupportError

    def __check_manager_user(self):
        self.__check_user()
        if not self._user.is_manager():
            raise UserNotSupportError

    def get_user_info(self):
        self.__check_user()
        return self._user.get_info()

    def get_user_info_no_update(self) -> Dict[str, str]:
        if not self.check_user():
            return {}
        return self._user.get_info()

    def scan(self) -> Tuple[int, any]:
        """
        处理扫码事务
        二维码扫描的任务包括: 登录, 扔垃圾, 标记垃圾
        :return:
        """
        self._cap.get_image()
        qr_code = self._qr.get_qr_code()
        if qr_code is None:
            return ControlScanType.no_to_done, None

        user: Optional[User] = scan_user(qr_code, self._db)
        if user is not None:
            return ControlScanType.switch_user, user

        garbage: Optional[GarbageBag] = scan_garbage(qr_code, self._db)
        if garbage is not None:
            if self._user is None:
                raise ControlNotLogin
            if self._user.is_manager():
                return ControlScanType.check_garbage, garbage
            return ControlScanType.throw_garbage, garbage

        return ControlScanType.no_to_done, None

    def get_cap_img(self):
        return self._cap.get_frame()

    def switch_user(self, user: User) -> bool:
        """
        切换用户: 退出/登录
        :param user: 新用户
        :return: 登录-True, 退出-False
        """
        if self._user is not None and self._user.get_uid() == user.get_uid() and self.check_user():  # 正在登陆期
            self._user = None  # 退出登录
            self._user_last_time = 0
            return False
        self._user = user
        self._user_last_time = time.time()
        return True  # 登录

    def throw_garbage(self, garbage: GarbageBag, garbage_type: enum):
        self.__check_normal_user()
        if not self._user.throw_rubbish(garbage, garbage_type, self._loc):
            raise ThrowGarbageError
        update_garbage(garbage, self._db)
        update_user(self._user, self._db)

    def check_garbage(self, garbage: GarbageBag, check_result: bool):
        self.__check_manager_user()
        user = find_user_by_id(garbage.get_user(), self._db)
        if user is None:
            raise GarbageBagNotUse
        if not self._user.check_rubbish(garbage, check_result, user):
            raise CheckGarbageError
        update_garbage(garbage, self._db)
        update_user(self._user, self._db)
        update_user(user, self._db)

    def creat_garbage(self, path: str, num: int = 1) -> List[tuple[str, Optional[GarbageBag]]]:
        self.__check_manager_user()
        if self._user is None:
            raise ControlNotLogin

        re = []
        for _ in range(num):
            gar = creat_new_garbage(self._db)
            if gar is None:
                raise CreatGarbageError
            res = write_gid_qr(gar.get_gid(), path, self._db)
            re.append(res)
        return re

    def creat_user(self, name: uname_t, passwd: passwd_t, phone: str, manager: bool) -> Optional[User]:
        user = creat_new_user(name, passwd, phone, manager, self._db)
        if user is None:
            raise CreatUserError
        return user

    def creat_user_from_list(self, user_list: List[Tuple[uname_t, passwd_t, str]], manager: bool) -> List[User]:
        re = []
        for i in user_list:
            user = creat_new_user(i[0], i[1], i[2], manager, self._db)
            if user is None:
                raise CreatUserError
            re.append(user)
        return re


global_control = Control()
