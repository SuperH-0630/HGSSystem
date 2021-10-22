import time

from tool.type_ import *
from sql.db import DB
from sql.user import find_user_by_name, creat_new_user
from sql.garbage import creat_new_garbage

from core.user import User
from core.garbage import GarbageBag

from event import TkEventBase, TkThreading, TkEventException
import admin


class AdminEventBase(TkEventBase):
    def __init__(self, station):
        super(AdminEventBase, self).__init__()
        self.station: admin.AdminStationBase = station
        self._db: DB = station.get_db()

    def get_title(self) -> str:
        return "AdminEvent"


class LoginEvent(AdminEventBase):
    def __init__(self, station):
        super().__init__(station)
        self.thread: Optional[TkThreading] = None

    def login(self, name, passwd):
        return find_user_by_name(name, passwd, self._db)

    def start(self, name, passwd):
        self.thread = TkThreading(self.login, name, passwd)
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        self.station.login(self.thread.wait_event())


class TestProgressEvent(AdminEventBase):
    @staticmethod
    def func(sleep_time):
        time.sleep(sleep_time)

    def __init__(self, station):
        super(TestProgressEvent, self).__init__(station)
        self.thread = TkThreading(self.func, 5)


class CreatUserEvent(AdminEventBase):
    def func(self, name, passwd, phone, is_manager):
        return self.station.creat_user(name, passwd, phone, is_manager)

    def __init__(self, station):
        super(CreatUserEvent, self).__init__(station)
        self._name = None

    def start(self, name, passwd, phone, is_manager):
        self._name = name
        self.thread = TkThreading(self.func, name, passwd, phone, is_manager)
        return self

    def done_after_event(self):
        res: Optional[User] = self.thread.wait_event()
        if res is None:
            self.station.show_msg("CreatUserError", f"Can't not creat user: {self._name}", "Warning")
        else:
            name = res.get_name()
            self.station.show_msg("CreatUser", f"Creat user {name} success")


class CreatGarbageEvent(AdminEventBase):
    def func(self, path, count):
        return self.station.creat_garbage(path, count)

    def __init__(self, station):
        super(CreatGarbageEvent, self).__init__(station)
        self._name = None

    def start(self, path, count):
        self.thread = TkThreading(self.func, path, count)
        return self

    def done_after_event(self):
        res: list[tuple[str, Optional[GarbageBag]]] = self.thread.wait_event()
        self.station.show_msg("CreatGarbage", f"Creat {len(res)} garbage finished.")


class DelUserEvent(AdminEventBase):
    def func(self, uid):
        return self.station.del_user(uid)

    def __init__(self, station):
        super(DelUserEvent, self).__init__(station)
        self._name = None

    def start(self, uid):
        self.thread = TkThreading(self.func, uid)
        return self

    def done_after_event(self):
        res: bool = self.thread.wait_event()
        if res:
            self.station.show_msg("DeleteUser", f"Delete user finished.")
        else:
            self.station.show_msg("DeleteUserError", f"Delete user failed.", "Warning")


class DelUserFromWhereScanEvent(AdminEventBase):
    def func(self, where):
        return self.station.del_user_from_where_scan(where)

    def __init__(self, station):
        super(DelUserFromWhereScanEvent, self).__init__(station)

    def start(self, where):
        self.thread = TkThreading(self.func, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("DeleteUserScan", f"Delete count: {res}")
        else:
            self.station.show_msg("DeleteUserScanError", f"`Where` must be SQL")


class DelUserFromWhereEvent(AdminEventBase):
    def func(self, where):
        return self.station.del_user_from_where(where)

    def __init__(self, station):
        super(DelUserFromWhereEvent, self).__init__(station)

    def start(self, where):
        self.thread = TkThreading(self.func, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("DeleteUser", f"Delete {res} user success")
        else:
            self.station.show_msg("DeleteUserError", f"`Where` must be SQL")
