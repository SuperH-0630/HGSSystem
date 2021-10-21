import threading

from tool.type_ import *
from tool.time_ import HGSTime, hgs_time_t
from tool.location import HGSLocation, hgs_location_t


class GarbageBagNotUse(Exception):
    pass


class GarbageType:
    GarbageTypeStrList: List = ["", "recyclable", "kitchen", "hazardous", "other"]
    recyclable: enum = 1
    kitchen: enum = 2
    hazardous: enum = 3
    other: enum = 4


class GarbageBag:
    def __init__(self, gid: gid_t):
        self._gid: gid_t = gid
        self._have_use: bool = False
        self._have_check: bool = False

        self._type: Union[enum, None] = None
        self._use_time: Union[HGSTime, None] = None
        self._user: Union[uid_t, None] = None
        self._loc: Union[HGSLocation, None] = None

        self._check = False
        self._checker: Union[uid_t, None] = None

        self._lock = threading.RLock()

    def __repr__(self):
        tmp = GarbageType.GarbageTypeStrList

        try:
            self._lock.acquire()
            if not self._have_use:
                info = f"GarbageBag: {self._gid} NOT USE"
            elif not self._have_check:
                info = (f"GarbageBag: {self._gid} "
                        f"Type: {tmp[self._type]} "
                        f"Time: {self._use_time.get_time()} "
                        f"User: {self._user} "
                        f"Location {self._loc.get_location()} "
                        f"NOT CHECK")
            else:
                info = (f"GarbageBag: {self._gid} "
                        f"Type: {tmp[self._type]} "
                        f"Time: {self._use_time.get_time()} "
                        f"User: {self._user} "
                        f"Location {self._loc.get_location()} "
                        f"Check: {self._check}"
                        f"Checker: {self._checker}")
        finally:
            self._lock.release()
        return info

    def get_info(self) -> dict[str: str]:
        try:
            self._lock.acquire()
            info = {
                "gid": str(self._gid),
                "type": str(self._type),
                "use_time": "" if (self._use_time is None) else str(self._use_time.get_time()),
                "user": str(self._user),
                "loc": "" if (self._loc is None) else str(self._loc.get_location()),
                "check": 'Pass' if self._check else 'Fail',
                "checker": "None" if self._checker is None else self._checker,
            }
        finally:
            self._lock.release()
        return info

    def is_use(self) -> bool:
        try:
            self._lock.acquire()
            have_use = self._have_use
        finally:
            self._lock.release()
        return have_use

    def is_check(self) -> Tuple[bool, bool]:
        try:
            self._lock.acquire()
            have_check = self._have_check
            check = self._check
        finally:
            self._lock.release()

        if not have_check:
            return False, False
        else:
            return True, check

    def get_gid(self):
        try:
            self._lock.acquire()
            gid = self._gid
        finally:
            self._lock.release()

        return gid

    def get_user(self) -> uid_t:
        try:
            self._lock.acquire()
            user = self._user
            have_use = self._have_use
        finally:
            self._lock.release()

        if not have_use:
            raise GarbageBagNotUse
        return user

    def get_type(self):
        try:
            self._lock.acquire()
            type_ = self._type
            have_use = self._have_use
        finally:
            self._lock.release()

        if not have_use:
            raise GarbageBagNotUse
        return type_

    def config_use(self, garbage_type: enum, use_time: hgs_time_t, user: uid_t, location: hgs_location_t):
        try:
            self._lock.acquire()
            assert not self._have_use
            self._have_use = True
            if not isinstance(use_time, HGSTime):
                use_time = HGSTime(use_time)
            if not isinstance(location, HGSLocation):
                location = HGSLocation(location)
            self._type: enum = garbage_type
            self._use_time: HGSTime = use_time
            self._user: uid_t = user
            self._loc: HGSLocation = location
        finally:
            self._lock.release()

    def config_check(self, use_right: bool, check_uid: uid_t):
        try:
            self._lock.acquire()
            assert self._have_use
            assert not self._have_check
            self._have_check = True
            self._check = use_right
            self._checker = check_uid
        finally:
            self._lock.release()
