import time

from tool.type_ import *
from sql.db import DB
from sql.user import find_user_by_name

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

    def is_end(self) -> bool:
        return not self.thread.is_alive()
