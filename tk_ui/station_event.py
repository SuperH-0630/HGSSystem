import tempfile

from equipment.scan import QRCode
from equipment.scan_user import scan_user
from equipment.scan_garbage import scan_garbage

from tool.type_ import *

from core.user import User
from core.garbage import GarbageBag

from sql.db import DB

from .event import TkThreading, TkEventBase
from . import station as tk_station


class StationEventBase(TkEventBase):
    def __init__(self, station: tk_station.GarbageStationBase, title: str = '未知'):
        super(StationEventBase, self).__init__()
        self.station: tk_station.GarbageStationBase = station
        self._db: DB = station.get_db()
        self._title = title

    def get_title(self) -> str:
        return self._title


class ScanUserEvent(StationEventBase):
    """
    任务: 扫码用户, 访问db获取数据
    若QR-CODE不是User码则调用ScanGarbage任务
    """

    @staticmethod
    def func(qr: QRCode, db: DB):
        return scan_user(qr, db)

    def __init__(self, gb_station):
        super().__init__(gb_station, "扫码用户")

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
    """
    任务: 扫码垃圾袋, 访问db获取数据
    """

    @staticmethod
    def func(qr: QRCode, db: DB):
        return scan_garbage(qr, db)

    def __init__(self, gb_station):
        super().__init__(gb_station, "扫码垃圾袋")

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
                self.station.show_warning("操作失败", "垃圾袋已经被使用")
            elif self._user.is_manager():
                self.station.to_get_garbage_check(self.thread.result)
                self.station.show_garbage_info()  # 显示信息
                self.station.update_control()
            else:
                self.station.to_get_garbage_type(self.thread.result)
                self.station.hide_msg_rank()  # 如果有msg也马上隐藏
                self.station.update_control()


class RankingEvent(StationEventBase):
    """
    任务: 获取排行榜数据
    """

    @staticmethod
    def func(db: DB):
        cur = db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                        table='user',
                        where='IsManager=0',
                        order_by=[('Reputation', "DESC"), ('Score', "DESC"), ('UserID', "DESC")],
                        limit=20)
        if cur is None:
            return []
        return list(cur.fetchall())

    def __init__(self, gb_station):
        super().__init__(gb_station, "排行榜")
        self.thread = TkThreading(self.func, self._db)

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        res = self.thread.wait_event()
        if res is not None:
            self.station.thread_show_rank(res)
        else:
            self.station.show_warning("排行榜错误", f'无法获得排行榜数据')


class ThrowGarbageEvent(StationEventBase):
    """
    任务: 提交扔垃圾的结果
    """

    def func(self, garbage: GarbageBag, garbage_type: enum):
        return self.station.throw_garbage_core(garbage, garbage_type)

    def __init__(self, gb_station):
        super().__init__(gb_station, "垃圾投放")

        self.thread = None

    def start(self, garbage: GarbageBag, garbage_type: enum):
        self.thread = TkThreading(self.func, garbage, garbage_type)
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        res = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("垃圾投放", "管理员用户不得投放垃圾", show_time=3.0)
        elif res == -2:
            self.station.show_warning("垃圾投放", "垃圾投放失败", show_time=3.0)
        elif res == -3:
            self.station.show_warning("垃圾投放", "数据库操作失败", show_time=3.0)
        else:
            self.station.show_msg("操作成功", "垃圾袋完成投放", show_time=3.0)


class CheckGarbageEvent(StationEventBase):
    """
    任务: 提交检测垃圾的结果
    """

    def func(self, garbage: GarbageBag, check: bool):
        return self.station.check_garbage_core(garbage, check)

    def __init__(self, gb_station):
        super().__init__(gb_station, "检测垃圾袋")
        self.thread = None

    def start(self, garbage: GarbageBag, garbage_check: bool):
        self.thread = TkThreading(self.func, garbage, garbage_check)
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        res = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("垃圾投放", "非管理员用户不得检查垃圾", show_time=3.0)
        elif res == -2:
            self.station.show_warning("垃圾检测", "垃圾袋还未使用", show_time=3.0)
        elif res == -3:
            self.station.show_warning("垃圾检测", "垃圾检测提结果交失败", show_time=3.0)
        elif res == -4:
            self.station.show_warning("垃圾检测", "数据库操作失败", show_time=3.0)
        else:
            self.station.show_msg("垃圾检测", "垃圾检测提结果交成功", show_time=3.0)


class SearchGarbageEvent(StationEventBase):
    """
    任务: 搜索垃圾垃圾的结果
    """

    def func(self, temp_dir: tempfile.TemporaryDirectory, file_path: str):
        return self.station.search_core(temp_dir, file_path)

    def __init__(self, gb_station):
        super().__init__(gb_station, "搜索垃圾")
        self.thread = None

    def start(self, temp_dir: tempfile.TemporaryDirectory, file_path: str):
        self.thread = TkThreading(self.func, temp_dir, file_path)
        return self

    def is_end(self) -> bool:
        return not self.thread.is_alive()

    def done_after_event(self):
        res = self.thread.wait_event()
        if res is None:
            self.station.show_warning("垃圾搜索", "垃圾搜索发生错误")
        else:
            self.station.get_search_result(res)
