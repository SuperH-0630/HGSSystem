import time

from tool.type_ import *
from sql.db import DB
from sql.user import find_user_by_name

from core.user import User
from core.garbage import GarbageBag

from event import TkEventBase, TkThreading
import admin
import admin_program

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


class DelGarbageEvent(AdminEventBase):
    def func(self, gid, where):
        if where == 0:
            return 1 if self.station.del_garbage(gid) else -1
        elif where == 1:
            return 1 if self.station.del_garbage_not_use(gid) else -1
        elif where == 2:
            return 1 if self.station.del_garbage_wait_check(gid) else -1
        elif where == 3:
            return 1 if self.station.del_garbage_has_check(gid) else -1
        return -1

    def __init__(self, station):
        super(DelGarbageEvent, self).__init__(station)

    def start(self, gid, where):
        self.thread = TkThreading(self.func, gid, where)
        return self

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("DeleteGarbage", f"Delete {res} garbage success")
        else:
            self.station.show_msg("DeleteGarbageError", f"Delete error")


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
            self.station.show_msg("DeleteGarbage", f"Delete {res} garbage success")
        else:
            self.station.show_msg("DeleteGarbageError", f"Delete error")


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
            self.station.show_msg("DeleteGarbageScan", f"Delete count: {res}")
        else:
            self.station.show_msg("DeleteGarbageScanError", f"Delete scan error")


class DelAllGarbageScanEvent(AdminEventBase):
    def func(self):
        return self.station.del_all_garbage_scan()

    def __init__(self, station):
        super(DelAllGarbageScanEvent, self).__init__(station)
        self.thread = TkThreading(self.func)

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("DeleteAllGarbageScan", f"Delete count: {res}")
        else:
            self.station.show_msg("DeleteAllGarbageError", f"Delete scan error")


class DelAllGarbageEvent(AdminEventBase):
    def func(self):
        return self.station.del_all_garbage()

    def __init__(self, station):
        super(DelAllGarbageEvent, self).__init__(station)
        self.thread = TkThreading(self.func)

    def done_after_event(self):
        res: int = self.thread.wait_event()
        if res != -1:
            self.station.show_msg("DeleteAllGarbage", f"Delete all[{res}] garbage success")
        else:
            self.station.show_msg("DeleteAllGarbageError", f"Delete error")


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
            self.station.show_msg("Search User Error", f"Search error")
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
            self.station.show_msg("Search User Advanced Error", f"Search error")
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
            self.station.show_msg("Search Garbage Advanced Error", f"Search error")
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
            self.station.show_msg("Search Advanced Error", f"Search error")
            return
        for i in self.program.view.get_children():
            self.program.view.delete(i)
        for i in res:
            self.program.view.insert('', 'end', values=i)
