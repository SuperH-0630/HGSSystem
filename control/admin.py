import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import tkinter.font as font
import abc

import conf
from tool.type_ import *

from sql.db import DB
from sql.user import creat_new_user, del_user, find_user_by_name
from sql.garbage import creat_new_garbage, del_garbage_not_use, del_garbage_not_use_many

from equipment.scan_user import write_uid_qr, write_all_uid_qr
from equipment.scan_garbage import write_gid_qr

from core.user import User
from core.garbage import GarbageBag

from tk_event import TkEventBase, TkEventMain, TkThreading


class AdminStationException(Exception):
    ...


class CreatGarbageError(AdminStationException):
    ...


class CreatUserError(AdminStationException):
    ...


class AdminEventBase(TkEventBase):
    def __init__(self, station, db: DB, title: str = 'unknown'):
        self.station: AdminStationBase = station
        self._db: DB = db
        self._title = title

    def get_title(self) -> str:
        return self._title

    def is_end(self) -> bool:
        raise AdminStationException

    def done_after_event(self):
        raise AdminStationException


class AdminStationBase(TkEventMain, metaclass=abc.ABCMeta):
    def __init__(self, db: DB):
        self._admin: Optional[User] = None
        self._db = db
        super(AdminStationBase, self).__init__()

    def creat_garbage(self, path: str, num: int = 1) -> List[tuple[str, Optional[GarbageBag]]]:
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

    def get_gid_qrcode(self, gid: gid_t, path: str) -> Tuple[str, Optional[GarbageBag]]:
        return write_gid_qr(gid, path, self._db)

    def get_all_gid_qrcode(self, path: str, where: str = "") -> List[str]:
        return write_all_uid_qr(path, self._db, where=where)

    def get_uid_qrcode(self, uid: uid_t, path: str) -> Tuple[str, Optional[User]]:
        return write_uid_qr(uid, path, self._db)

    def get_all_uid_qrcode(self, path: str, where: str = "") -> List[str]:
        return write_all_uid_qr(path, self._db, where=where)

    def del_garbage(self, gid: gid_t) -> bool:
        return del_garbage_not_use(gid, self._db)

    def del_garbage_many(self, from_: gid_t, to_: gid_t) -> int:
        return del_garbage_not_use_many(from_, to_, self._db)

    def del_user(self, uid: uid_t) -> bool:
        return del_user(uid, self._db)

    @abc.abstractmethod
    def login_call(self):
        ...

    def login(self, user: User) -> bool:
        if user is not None and user.is_manager():
            self._admin = user
            return True
        else:
            return False

    @abc.abstractmethod
    def show_loading(self, title: str):
        ...

    @abc.abstractmethod
    def stop_loading(self):
        ...

    @abc.abstractmethod
    def set_after_run(self, ms, func, *args):
        ...


class AdminStation(AdminStationBase):
    def set_after_run(self, ms, func, *args):  # super.__init__可能会调用
        self.init_after_run_list.append((ms, func, args))

    def __conf_set_after_run(self):
        for ms, func, args in self.init_after_run_list:
            self._window.after(ms, func, *args)

    def set_after_run_now(self, ms, func, *args):
        self._window.after(ms, func, *args)

    def __init__(self, db: DB, refresh_delay: int = conf.tk_refresh_delay):
        self.init_after_run_list: List[Tuple[int, Callable, Tuple]] = []

        super().__init__(db)
        self.refresh_delay = refresh_delay

        self._window = tk.Tk()
        self.login_window = None
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))
        self._win_width = int(self._sys_width * (2 / 3))

        self._full_screen = False
        self.__conf_windows()

        self.__conf_font_size()
        self.__show_login_window()
        self.__conf_set_after_run()

    def __conf_windows(self):
        self._window.title('HGSSystem: Manage Station')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = "#F0FFF0"
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", lambda: self.main_exit())

    def __conf_creak_tk(self):
        self._frame_list: List[AdminMenu] = []
        self._program_frame: List[AdminProgram] = []

        self._msg_frame = tk.Frame(self._window)
        self._msg_label = tk.Label(self._msg_frame), tk.Label(self._msg_frame), tk.StringVar(), tk.StringVar()
        self._msg_hide = tk.Button(self._msg_frame)

        self._loading_frame = tk.Frame(self._window)
        self._loading_title: Tuple[tk.Label, tk.Variable] = tk.Label(self._loading_frame), tk.StringVar()
        self._loading_pro = ttk.Progressbar(self._loading_frame)

    def __conf_font_size(self, n: int = 1):
        self._login_title_font_size = int(12 * n)
        self._login_btn_font_size = int(11 * n)

    def __show_login_window(self):
        self.login_window: Optional[tk.Toplevel] = tk.Toplevel()
        self.login_window.title("HGSSystem Login")

        height = int(self._sys_height * (1 / 6))
        width = int(height * 2)

        if width > self._sys_width:
            width = int(self._sys_width * (2 / 3))
            height = int(width / 2)

        self.login_window.geometry(f'{width}x{height}')
        self.login_window['bg'] = "#d1d9e0"
        self.login_window.resizable(False, False)
        self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.login_exit())
        self._login_name = [tk.Label(self.login_window), tk.Entry(self.login_window), tk.StringVar()]
        self._login_passwd = [tk.Label(self.login_window), tk.Entry(self.login_window), tk.StringVar()]
        self._login_btn = [tk.Button(self.login_window), tk.Button(self.login_window)]

        self.__conf_login_window()
        self.hide_main()

    def __conf_login_window(self):
        title_font = self.__make_font(size=self._login_title_font_size, weight="bold")
        btn_font = self.__make_font(size=self._login_btn_font_size, weight="bold")

        for lb, text in zip([self._login_name[0], self._login_passwd[0]], ["User:", "Passwd:"]):
            lb['bg'] = "#d1d9e0"  # 蜜瓜绿
            lb['font'] = title_font
            lb['text'] = text
            lb['anchor'] = 'e'

        for lb, var in zip([self._login_name[1], self._login_passwd[1]], [self._login_name[2], self._login_passwd[2]]):
            lb['font'] = title_font
            lb['textvariable'] = var

        self._login_name[0].place(relx=0.00, rely=0.20, relwidth=0.35, relheight=0.15)
        self._login_passwd[0].place(relx=0.00, rely=0.40, relwidth=0.35, relheight=0.15)

        self._login_name[1].place(relx=0.40, rely=0.20, relwidth=0.45, relheight=0.15)
        self._login_passwd[1]['show'] = "*"
        self._login_passwd[1].place(relx=0.40, rely=0.40, relwidth=0.45, relheight=0.15)

        self._login_btn[0]['bg'] = "#a1afc9"
        self._login_btn[0]['font'] = btn_font
        self._login_btn[0]['text'] = 'Login'
        self._login_btn[0]['command'] = lambda: self.login_call()
        self._login_btn[0].place(relx=0.50, rely=0.70, relwidth=0.16, relheight=0.15)

        self._login_btn[1]['bg'] = "#a1afc9"
        self._login_btn[1]['font'] = btn_font
        self._login_btn[1]['text'] = 'Exit'
        self._login_btn[1]['command'] = lambda: self.login_exit()
        self._login_btn[1].place(relx=0.70, rely=0.70, relwidth=0.16, relheight=0.15)

    def login_call(self):
        event = LoginEvent(self, self._db).start(self._login_name[2].get(),
                                                 self._login_passwd[2].get())
        self.push_event(event)

    def login(self, user: User):
        if super(AdminStation, self).login(user):
            self.login_window.destroy()
            self.login_window = None
            self.show_main()
        else:
            msg.showerror("Login error", "Please, try again")
            self._login_name[2].set('')
            self._login_passwd[2].set('')

    def login_exit(self):
        if not msg.askokcancel('Sure?', 'Exit manager system.'):
            return
        if self.login_window is not None:
            self.login_window.destroy()
        self.exit_win()

    def main_exit(self):
        if not msg.askokcancel('Sure?', 'Exit manager system.'):
            return
        self.exit_win()

    def hide_main(self):
        self._window.withdraw()

    def show_main(self):
        self._window.update()
        self._window.deiconify()

    def show_loading(self, title: str):
        ...

    def stop_loading(self):
        ...

    @staticmethod
    def __make_font(family: str = 'noto', **kwargs):
        return font.Font(family=conf.font_d[family], **kwargs)

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()


class LoginEvent(AdminEventBase):
    def __init__(self, station: AdminStationBase, db: DB):
        super().__init__(station, db, "Ranking")
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


class AdminMenu(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_menu_frame(self, station: AdminStation) -> tk.Frame:
        ...


class AdminProgram(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_admin_frame(self, station: AdminStation) -> tk.Frame:
        ...


if __name__ == '__main__':
    mysql_db = DB()
    station_ = AdminStation(mysql_db)
    station_.mainloop()
