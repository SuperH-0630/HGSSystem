import time

from tool.type_ import *
from sql.db import DB
from sql.user import find_user_by_name

from core.user import User
from core.garbage import GarbageBag

from .event import TkEventBase, TkThreading
from . import admin
from . import admin_program


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


class CreateUserEvent(AdminEventBase):
    def func(self, name, passwd, phone, is_manager):
        return self.station.create_user(name, passwd, phone, is_manager)

    def __init__(self, station):
        super(CreateUserEvent, self).__init__(station)
        self._name = None

    def start(self, name, passwd, phone, is_manager):
        self._name = name
        self.thread = TkThreading(self.func, name, passwd, phone, is_manager)
        return self

    def done_after_event(self):
        res: Optional[User] = self.thread.wait_event()
        if res is None:
            self.station.show_warning("创建用户错误", f"无法创建用户 user: {self._name}")
        else:
            name = res.get_name()
            self.station.show_msg("创建用户成功", f"成功创建{name}个新用户")


class CreateGarbageEvent(AdminEventBase):
    def func(self, path, count):
        return self.station.create_garbage(path, count)

    def __init__(self, station):
        super(CreateGarbageEvent, self).__init__(station)
        self._name = None

    def start(self, path, count):
        self.thread = TkThreading(self.func, path, count)
        return self

    def done_after_event(self):
        res: list[tuple[str, Optional[GarbageBag]]] = self.thread.wait_event()
        self.station.show_msg("创建垃圾袋", f"成功创建{len(res)}个垃圾袋")


class ExportGarbageByIDEvent(AdminEventBase):
    def func(self, path, gid):
        return self.station.export_garbage_by_gid(path, gid)

    def __init__(self, station):
        super(ExportGarbageByIDEvent, self).__init__(station)
        self._name = None

    def start(self, path, gid):
        self.thread = TkThreading(self.func, path, gid)
        return self

    def done_after_event(self):
        res: tuple[str, Optional[GarbageBag]] = self.thread.wait_event()
        if res[1] is None:
            self.station.show_warning("导出错误", f"无法导出垃圾袋二维码")
        else:
            self.station.show_msg("导出成功", f"成功导出垃圾袋二维码")


class ExportGarbageAdvancedEvent(AdminEventBase):
    def func(self, path, where):
        return self.station.export_garbage(path, where)

    def __init__(self, station):
        super(ExportGarbageAdvancedEvent, self).__init__(station)
        self._name = None

    def start(self, path, where):
        self.thread = TkThreading(self.func, path, where)
        return self

    def done_after_event(self):
        res: list[tuple[str]] = self.thread.wait_event()
        self.station.show_msg("导出完成", f"导出{len(res)}个垃圾袋二维码")


class ExportUserByIDEvent(AdminEventBase):
    def func(self, path, uid):
        return self.station.export_user_by_uid(path, uid)

    def __init__(self, station):
        super(ExportUserByIDEvent, self).__init__(station)
        self._name = None

    def start(self, path, uid):
        self.thread = TkThreading(self.func, path, uid)
        return self

    def done_after_event(self):
        res: tuple[str, Optional[GarbageBag]] = self.thread.wait_event()
        if res[1] is None:
            self.station.show_warning("导出错误", f"无法导出用户二维码")
        else:
            self.station.show_msg("导出成功", f"成功导出用户二维码")


class ExportUserAdvancedEvent(AdminEventBase):
    def func(self, path, where):
        return self.station.export_user(path, where)

    def __init__(self, station):
        super(ExportUserAdvancedEvent, self).__init__(station)
        self._name = None

    def start(self, path, where):
        self.thread = TkThreading(self.func, path, where)
        return self

    def done_after_event(self):
        res: list[tuple[str]] = self.thread.wait_event()
        self.station.show_msg("导出完成", f"导出{len(res)}个用户二维码")


class CreateUserFromCSVEvent(AdminEventBase):
    def func(self, path):
        return self.station.create_user_from_csv(path)

    def __init__(self, station):
        super(CreateUserFromCSVEvent, self).__init__(station)
        self._name = None

    def start(self, path):
        self.thread = TkThreading(self.func, path)
        return self

    def done_after_event(self):
        res: list[User] = self.thread.wait_event()
        self.station.show_msg("创建完成", f"从CSV创建{len(res)}个新用户")


class CreateAutoUserFromCSVEvent(AdminEventBase):
    def func(self, path):
        return self.station.create_auto_user_from_csv(path)

    def __init__(self, station):
        super(CreateAutoUserFromCSVEvent, self).__init__(station)
        self._name = None

    def start(self, path):
        self.thread = TkThreading(self.func, path)
        return self

    def done_after_event(self):
        res: list[User] = self.thread.wait_event()
        self.station.show_msg("创建完成", f"从CSV创建{len(res)}个新用户")


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
            self.station.show_msg("删除成功", f"删除用户成功")
        else:
            self.station.show_warning("删除失败", f"删除用户失败")


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
            self.station.show_msg("扫描结果", f"符合删除要素的用户个数: {res}")
        else:
            self.station.show_warning("扫描结果", f"获取扫描结果失败")


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
            self.station.show_msg("扫描结果", f"成功删除{res}个用户")
        else:
            self.station.show_warning("扫描结果", f"获取扫描结果失败")


class DelGarbageEvent(AdminEventBase):
    def func(self, gid, where):
        if where == 0:
            return self.station.del_garbage(gid)
        elif where == 1:
            return self.station.del_garbage_not_use(gid)
        elif where == 2:
            return self.station.del_garbage_wait_check(gid)
        elif where == 3:
            return self.station.del_garbage_has_check(gid)
        return False

    def __init__(self, station):
        super(DelGarbageEvent, self).__init__(station)

    def start(self, gid, where):
        self.thread = TkThreading(self.func, gid, where)
        return self

    def done_after_event(self):
        res: bool = self.thread.wait_event()
        if res:
            self.station.show_msg("删除成功", f"成功删除垃圾袋")
        else:
            self.station.show_warning("删除失败", f"删除垃圾袋失败")


class DelGarbageWhereEvent(AdminEventBase):
    def func(self, where, where_sql):
        if where == 1:
            return self.station.del_garbage_where_not_use(where_sql)
        elif where == 2:
            return self.station.del_garbage_where_wait_check(where_sql)
        elif where == 3:
            return self.station.del_garbage_where_has_check(where_sql)
        return -1

    def __init__(self, station):
        super(DelGarbageWhereEvent, self).__init__(station)

    def start(self, where, where_sql):
        self.thread = TkThreading(self.func, where, where_sql)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("删除成功", f"成功删除{res}个垃圾袋")
        else:
            self.station.show_warning("删除失败", f"垃圾袋删除失败")


class DelGarbageWhereScanEvent(AdminEventBase):
    def func(self, where, where_sql):
        if where == 1:
            return self.station.del_garbage_where_scan_not_use(where_sql)
        elif where == 2:
            return self.station.del_garbage_where_scan_wait_check(where_sql)
        elif where == 3:
            return self.station.del_garbage_where_scan_has_check(where_sql)
        return -1

    def __init__(self, station):
        super(DelGarbageWhereScanEvent, self).__init__(station)

    def start(self, where, where_sql):
        self.thread = TkThreading(self.func, where, where_sql)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("扫描结果", f"符合删除要素的垃圾袋个数: {res}")
        else:
            self.station.show_warning("扫描结果", f"获取扫描结果失败")


class DelAllGarbageScanEvent(AdminEventBase):
    def func(self):
        return self.station.del_all_garbage_scan()

    def __init__(self, station):
        super(DelAllGarbageScanEvent, self).__init__(station)
        self.thread = TkThreading(self.func)

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("扫描结果", f"全部垃圾袋个数: {res}")
        else:
            self.station.show_warning("扫描结果", f"获取扫描结果失败")


class DelAllGarbageEvent(AdminEventBase):
    def func(self):
        return self.station.del_all_garbage()

    def __init__(self, station):
        super(DelAllGarbageEvent, self).__init__(station)
        self.thread = TkThreading(self.func)

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("删除成功", f"成功删除所用[共计{res}个]垃圾袋")
        else:
            self.station.show_warning("删除失败", f"删除所有垃圾袋失败")


class SearchUserEvent(AdminEventBase):
    def func(self, columns, uid, name, phone):
        return self.station.search_user(columns, uid, name, phone)

    def __init__(self, station):
        super(SearchUserEvent, self).__init__(station)
        self.program: Optional[admin_program.SearchUserProgram] = None

    def start(self, columns, uid, name, phone, program):
        self.thread = TkThreading(self.func, columns, uid, name, phone)
        self.program = program
        return self

    def done_after_event(self):
        res: list[list] = self.thread.wait_event()
        if res is None or self.program is None:
            self.station.show_warning("搜索失败", f"搜索用户失败")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)


class SearchUserAdvancedEvent(AdminEventBase):
    def func(self, columns, sql):
        return self.station.search_user_advanced(columns, sql)

    def __init__(self, station):
        super(SearchUserAdvancedEvent, self).__init__(station)
        self.program: Optional[admin_program.SearchUserAdvancedProgram] = None

    def start(self, columns, sql, program):
        self.thread = TkThreading(self.func, columns, sql)
        self.program = program
        return self

    def done_after_event(self):
        res: list[list] = self.thread.wait_event()
        if res is None or self.program is None:
            self.station.show_warning("高级搜索失败", f"高级搜索用户失败")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)


class SearchGarbageEvent(AdminEventBase):
    def func(self, columns, key_values: dict):
        return self.station.search_garbage(columns, key_values)

    def __init__(self, station):
        super(SearchGarbageEvent, self).__init__(station)
        self.program: Optional[admin_program.SearchUserProgram] = None

    def start(self, columns, key_values: dict, program):
        self.thread = TkThreading(self.func, columns, key_values)
        self.program = program
        return self

    def done_after_event(self):
        res: list[list] = self.thread.wait_event()
        if res is None or self.program is None:
            self.station.show_warning("搜索失败", f"搜索垃圾袋失败")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)


class SearchGarbageAdvancedEvent(AdminEventBase):
    def func(self, columns, sql):
        return self.station.search_garbage_advanced(columns, sql)

    def __init__(self, station):
        super(SearchGarbageAdvancedEvent, self).__init__(station)
        self.program: Optional[admin_program.SearchGarbageAdvancedProgram] = None

    def start(self, columns, sql, program):
        self.thread = TkThreading(self.func, columns, sql)
        self.program = program
        return self

    def done_after_event(self):
        res: list[list] = self.thread.wait_event()
        if res is None or self.program is None:
            self.station.show_warning("高级搜索失败", f"高级搜索垃圾袋失败")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)


class SearchAdvancedEvent(AdminEventBase):
    def func(self, columns, sql):
        return self.station.search_advanced(columns, sql)

    def __init__(self, station):
        super(SearchAdvancedEvent, self).__init__(station)
        self.program: Optional[admin_program.SearchAdvancedProgram] = None

    def start(self, columns, sql, program):
        self.thread = TkThreading(self.func, columns, sql)
        self.program = program
        return self

    def done_after_event(self):
        res: list[list] = self.thread.wait_event()
        if res is None or self.program is None:
            self.station.show_warning("高级搜索失败", f"高级搜索失败")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)


class UpdateUserScoreEvent(AdminEventBase):
    def func(self, score, where):
        return self.station.update_user_score(score, where)

    def __init__(self, station):
        super(UpdateUserScoreEvent, self).__init__(station)

    def start(self, score, where):
        self.thread = TkThreading(self.func, score, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("更新失败", f"更新用户-积分失败")
        else:
            self.station.show_msg("更新成功", f"成功更新{res}个用户-积分")


class UpdateUserReputationEvent(AdminEventBase):
    def func(self, reputation, where):
        return self.station.update_user_reputation(reputation, where)

    def __init__(self, station):
        super(UpdateUserReputationEvent, self).__init__(station)

    def start(self, reputation, where):
        self.thread = TkThreading(self.func, reputation, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("更新失败", f"更新用户-垃圾分类信用失败")
        else:
            self.station.show_msg("更新成功", f"成功更新{res}个用户-垃圾分类信用")


class UpdateGarbageTypeEvent(AdminEventBase):
    def func(self, type_, where):
        return self.station.update_garbage_type(type_, where)

    def __init__(self, station):
        super(UpdateGarbageTypeEvent, self).__init__(station)

    def start(self, type_, where):
        self.thread = TkThreading(self.func, type_, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("更新失败", f"更新垃圾袋-垃圾类型失败")
        else:
            self.station.show_msg("更新成功", f"成功更新{res}个垃圾袋-垃圾类型")


class UpdateGarbageCheckEvent(AdminEventBase):
    def func(self, check, where):
        return self.station.update_garbage_check(check, where)

    def __init__(self, station):
        super(UpdateGarbageCheckEvent, self).__init__(station)

    def start(self, check, where):
        self.thread = TkThreading(self.func, check, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res == -1:
            self.station.show_warning("更新失败", f"更新垃圾袋-检测结果失败")
        else:
            self.station.show_msg("更新成功", f"成功更新{res}个垃圾袋-检测结果")
