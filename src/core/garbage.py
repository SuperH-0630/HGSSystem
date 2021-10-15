from tool.time_ import HGSTime, hgs_time_t
from tool.location import HGSLocation, hgs_location_t
from tool.type_ import *
from enum import Enum


class GarbageBagNotUse(Exception):
    pass


class GarbageType(Enum):
    recyclable: enum = 1
    kitchen: enum = 2
    hazardous: enum = 3
    other: enum = 4


class GarbageBag:
    def __init__(self, gid: gid_t, last_time: time_t):
        self._gid: gid_t = gid
        self._have_use: bool = False
        self.last_time: HGSTime = HGSTime(last_time)

        self._type: Union[enum, None] = None
        self._use_time: Union[HGSTime, None] = None
        self._user: Union[uid_t, None] = None
        self._loc: Union[HGSLocation, None] = None

    def is_use(self) -> bool:
        return self._have_use

    def get_user(self) -> uid_t:
        if not self._have_use:
            raise GarbageBagNotUse
        return self._user

    def config_use(self, garbage_type: enum, use_time: hgs_time_t, user: uid_t, location: hgs_location_t):
        self._have_use = True
        if not isinstance(use_time, HGSTime):
            use_time = HGSTime(use_time)
        if not isinstance(location, HGSLocation):
            location = HGSLocation(location)
        self._type: enum = garbage_type
        self._use_time: enum = use_time
        self._user: enum = user
        self._loc: enum = location

    def is_out_of_date(self) -> bool:
        return self.last_time.is_out_of_date()
