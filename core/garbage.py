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

    def __repr__(self):
        tmp = GarbageType.GarbageTypeStrList
        if not self._have_use:
            return f"GarbageBag: {self._gid} NOT USE"
        elif not self._have_check:
            return (f"GarbageBag: {self._gid} "
                    f"Type: {tmp[self._type]} "
                    f"Time: {self._use_time.get_time()} "
                    f"User: {self._user} "
                    f"Location {self._loc.get_location()} "
                    f"NOT CHECK")
        return (f"GarbageBag: {self._gid} "
                f"Type: {tmp[self._type]} "
                f"Time: {self._use_time.get_time()} "
                f"User: {self._user} "
                f"Location {self._loc.get_location()} "
                f"Check: {self._check}"
                f"Checker: {self._checker}")

    def get_info(self) -> dict[str: str]:
        return {
            "gid":      str(self._gid),
            "type":     str(self._type),
            "use_time": (self._use_time is None) if "" else str(self._use_time.get_time()),
            "user":     str(self._user),
            "loc":      (self._loc is None) if "" else str(self._loc.get_location()),
            "check":    self._check if '1' else '0',
            "checker":  str(self._checker),
        }

    def is_use(self) -> bool:
        return self._have_use

    def is_check(self) -> Tuple[bool, bool]:
        if not self._have_check:
            return False, False
        else:
            return True, self._check

    def get_gid(self):
        return self._gid

    def get_user(self) -> uid_t:
        if not self._have_use:
            raise GarbageBagNotUse
        return self._user

    def get_type(self):
        if not self._have_use:
            raise GarbageBagNotUse
        return self._type

    def config_use(self, garbage_type: enum, use_time: hgs_time_t, user: uid_t, location: hgs_location_t):
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

    def config_check(self, use_right: bool, check_uid: uid_t):
        assert self._have_use
        assert not self._have_check
        self._have_check = True
        self._check = use_right
        self._checker = check_uid
