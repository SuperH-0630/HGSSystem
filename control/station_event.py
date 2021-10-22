from equipment.scan import QRCode
from equipment.scan_user import scan_user
from equipment.scan_garbage import scan_garbage

from tool.type_ import *

from core.user import User, UserNotSupportError
from core.garbage import GarbageBag

from sql.db import DB

from event import TkThreading, TkEventBase
import station as tk_station


class StationEventBase(TkEventBase):
    def __init__(self, station: tk_station.GarbageStationBase, title: str = 'unknown'):
        super(StationEventBase, self).__init__()
        self.station: tk_station.GarbageStationBase = station
        self._db: DB = station.get_db()
        self._title = title

    def get_title(self) -> str:
        return self._title

    def is_end(self) -> bool:
        raise tk_station.GarbageStationException

    def done_after_event(self):
        raise tk_station.GarbageStationException


class ScanUserEvent(StationEventBase):
    @staticmethod
    def func(qr: QRCode, db: DB):
        return scan_user(qr, db)

    def __init__(self, gb_station):
        super().__init__(gb_station, "Scan User")

        self._user: User = gb_station.get_user()
        self._qr_code: Optional[QRCode] = None
        self.thread = None

    def start(self, qr_code: QRCode):
        self._qr_code = qr_code
        self.thread = TkThreading(self.func, qr_code, self._db)
        return self

    def is_end(self) -> bool:
        return self.thread is not None and not self.thread.is_alive()

    def done_after_event(self):
        self.thread.join()
        if self.thread.result is not None:
            self.station.switch_user(self.thread.result)
            self.station.update_control()
        else:
            event = ScanGarbageEvent(self.station).start(self._qr_code)
            self.station.push_event(event)


class ScanGarbageEvent(StationEventBase):
    @staticmethod
    def func(qr: QRCode, db: DB):
        return scan_garbage(qr, db)

    def __init__(self, gb_station):
        super().__init__(gb_station, "Scan Garbage")

        self._user: User = gb_station.get_user()
        self._qr_code: Optional[QRCode] = None
        self.thread = None

    def start(self, qr_code: QRCode):
        self._qr_code = qr_code
        self.thread = TkThreading(self.func, qr_code, self._db)
        return self

    def is_end(self) -> bool:
        return self.thread is not None and not self.thread.is_alive()

    def done_after_event(self):
        self.thread.join()
        if self.thread.result is not None:
            if self._user is None:
                self.station.show_warning("Operation Fail", "The garbage bags have been used.")
            elif self._user.is_manager():
                self.station.to_get_garbage_check(self.thread.result)
                self.station.show_garbage_info()  # 显示信息
                self.station.update_control()
            else:
                self.station.to_get_garbage_type(self.thread.result)
                self.station.hide_msg_rank()  # 如果有msg也马上隐藏
                self.station.update_control()


class RankingEvent(StationEventBase):
    @staticmethod
    def func(db: DB):
        cur = db.search((f"SELECT uid, name, score, reputation "
                         f"FROM user "
                         f"WHERE manager = 0 "
                         f"ORDER BY reputation DESC, score DESC "
                         f"LIMIT 20;"))
        if cur is None:
            return []
        return list(cur.fetchall())

    def __init__(self, gb_station):
        super().__init__(gb_station, "Ranking")
        self.thread = TkThreading(self.func, self._db)

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        self.thread.join()
        if self.thread.result is not None:
            self.station.thread_show_rank(self.thread.result)


class ThrowGarbageEvent(StationEventBase):
    def func(self, garbage: GarbageBag, garbage_type: enum):
        try:
            self.station.throw_garbage_core(garbage, garbage_type)
        except (tk_station.ThrowGarbageError, UserNotSupportError, tk_station.ControlNotLogin):
            self.station.show_warning("Operation Fail", "The garbage bags have been used.")
            return False
        else:
            return True

    def __init__(self, gb_station):
        super().__init__(gb_station, "ThrowGarbage")

        self.thread = None

    def start(self, garbage: GarbageBag, garbage_type: enum):
        self.thread = TkThreading(self.func, garbage, garbage_type)
        self.thread.start()
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        self.thread.join()
        if not self.thread.result:
            self.station.show_warning("Operation Fail", "The garbage bag throw error")


class CheckGarbageEvent(StationEventBase):
    def func(self, garbage: GarbageBag, check: bool):
        try:
            self.station.check_garbage_core(garbage, check)
        except (tk_station.ThrowGarbageError, UserNotSupportError,
                tk_station.ControlNotLogin, tk_station.CheckGarbageError):
            self.station.show_warning("Operation Fail", "The garbage bag has been checked")
            return False
        else:
            return True

    def __init__(self, gb_station):
        super().__init__(gb_station, "CheckGarbage")
        self.thread = None

    def start(self, garbage: GarbageBag, garbage_check: bool):
        self.thread = TkThreading(self.func, garbage, garbage_check)
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        self.thread.join()
        if not self.thread.result:
            self.station.show_warning("Operation Fail", "The garbage bag check error")
