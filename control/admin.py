import abc
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk

import conf
from core.garbage import GarbageBag
from core.user import User
from equipment.scan_garbage import write_gid_qr
from equipment.scan_user import write_uid_qr, write_all_uid_qr
from event import TkEventMain
from sql.db import DB, search_from_garbage_checker_user
from sql.garbage import (creat_new_garbage, search_from_garbage_view,
                         del_garbage, del_garbage_not_use, del_garbage_wait_check, del_garbage_has_check,

                         del_garbage_where_scan_not_use, del_garbage_where_scan_wait_check,
                         del_garbage_where_scan_has_check,

                         del_garbage_where_not_use, del_garbage_where_wait_check, del_garbage_where_has_check,

                         del_garbage_not_use_many, del_all_garbage, del_all_garbage_scan)

from sql.user import (creat_new_user, del_user, del_user_from_where, del_user_from_where_scan,
                      search_user_by_fields, search_from_user_view)
from tool.tk import make_font
from tool.type_ import *


class AdminStationException(Exception):
    ...


class CreatGarbageError(AdminStationException):
    ...


class CreatUserError(AdminStationException):
    ...


class AdminStationBase(TkEventMain, metaclass=abc.ABCMeta):
    def __init__(self, db: DB):
        self._admin: Optional[User] = None
        self._db = db
        super(AdminStationBase, self).__init__()

    def get_db(self):
        return self._db

    def creat_garbage(self, path: Optional[str], num: int = 1) -> List[tuple[str, Optional[GarbageBag]]]:
        re = []
        for _ in range(num):
            gar = creat_new_garbage(self._db)
            if gar is None:
                raise CreatGarbageError
            if path is not None:
                res = write_gid_qr(gar.get_gid(), path, self._db)
                re.append(res)
            else:
                re.append(("", gar))
        return re

    def creat_user(self, name: uname_t, passwd: passwd_t, phone: str, manager: bool) -> Optional[User]:
        return creat_new_user(name, passwd, phone, manager, self._db)

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

    def del_garbage_not_use(self, gid: gid_t) -> bool:
        return del_garbage_not_use(gid, self._db)

    def del_garbage_wait_check(self, gid: gid_t) -> bool:
        return del_garbage_wait_check(gid, self._db)

    def del_garbage_has_check(self, gid: gid_t) -> bool:
        return del_garbage_has_check(gid, self._db)

    def del_garbage(self, gid: gid_t) -> bool:
        return del_garbage(gid, self._db)

    def del_garbage_where_not_use(self, where) -> int:
        return del_garbage_where_not_use(where, self._db)

    def del_garbage_where_wait_check(self, where) -> int:
        return del_garbage_where_wait_check(where, self._db)

    def del_garbage_where_has_check(self, where) -> int:
        return del_garbage_where_has_check(where, self._db)

    def del_garbage_where_scan_not_use(self, where) -> int:
        return del_garbage_where_scan_not_use(where, self._db)

    def del_garbage_where_scan_wait_check(self, where) -> int:
        return del_garbage_where_scan_wait_check(where, self._db)

    def del_garbage_where_scan_has_check(self, where) -> int:
        return del_garbage_where_scan_has_check(where, self._db)

    def del_all_garbage_scan(self) -> int:
        return del_all_garbage_scan(self._db)

    def del_all_garbage(self) -> int:
        return del_all_garbage(self._db)

    def del_garbage_many(self, from_: gid_t, to_: gid_t) -> int:
        return del_garbage_not_use_many(from_, to_, self._db)

    def del_user(self, uid: uid_t) -> bool:
        return del_user(uid, self._db)

    def del_user_from_where_scan(self, where: str) -> int:
        return del_user_from_where_scan(where, self._db)

    def del_user_from_where(self, where: str) -> int:
        return del_user_from_where(where, self._db)

    def search_user(self, columns, uid, name, phone):
        return search_user_by_fields(columns, uid, name, phone, self._db)

    def search_user_advanced(self, columns, sql):
        return search_from_user_view(columns, sql, self._db)

    def search_garbage_advanced(self, columns, sql):
        return search_from_garbage_view(columns, sql, self._db)

    def search_advanced(self, columns, sql):
        return search_from_garbage_checker_user(columns, sql, self._db)

    @abc.abstractmethod
    def login_call(self):
        ...

    def login(self, user: User) -> bool:
        if user is not None and user.is_manager():
            self._admin = user
            return True
        else:
            return False

    def logout(self):
        self._admin = None

    @abc.abstractmethod
    def show_loading(self, title: str):
        ...

    @abc.abstractmethod
    def stop_loading(self):
        ...

    @abc.abstractmethod
    def set_after_run(self, ms, func, *args):
        ...

    @abc.abstractmethod
    def to_menu(self, name: str = "Main"):
        ...

    @abc.abstractmethod
    def to_program(self, name: str = "Welcome"):
        ...

    @abc.abstractmethod
    def show_msg(self, title, info, msg_type='info'):
        ...

    @abc.abstractmethod
    def hide_msg(self):
        ...


import admin_program as tk_program
import admin_menu as tk_menu
import admin_event as tk_event


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
        self.__conf_windows()

        self._full_screen = False
        self._is_loading = False
        self._disable_all_btn = False
        self._menu_now: Optional[Tuple[str, tk.Frame, tk_menu.AdminMenu]] = None
        self._program_now: Optional[Tuple[str, tk.Frame, tk_program.AdminProgram]] = None

        self.__conf_font_size()
        self.__conf_create_tk()
        self.__conf_create_menu()
        self.__conf_create_program()
        self.__conf_tk()
        # self.__show_login_window()

        self.__conf_set_after_run()

    def __conf_windows(self):
        self._window.title('HGSSystem: Manage Station')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = "#F0FFF0"
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", lambda: self.main_exit())

    def __conf_create_tk(self):
        self._menu_back = tk.Frame(self._window)
        self._menu_line = tk.Label(self._menu_back)  # 下划线
        self._menu_title: Tuple[tk.Label, tk.Variable] = tk.Label(self._menu_back), tk.StringVar()
        self._menu_dict: Dict[str, tk_menu.AdminMenu] = {}
        self._menu_list: List[str] = []  # 菜单回溯

        self._program_back = tk.Frame(self._window)
        self._program_title: Tuple[tk.Label, tk.Variable] = tk.Label(self._program_back), tk.StringVar()
        self._program_dict: Dict[str, tk_program.AdminProgram] = {}

        self._win_ctrl_button: List[tk.Button, tk.Button, tk.Button] = [tk.Button(self._menu_back),
                                                                        tk.Button(self._menu_back),
                                                                        tk.Button(self._window),
                                                                        tk.Button(self._window),
                                                                        tk.Button(self._window)]

        self._msg_frame = tk.Frame(self._window)
        self._msg_label = tk.Label(self._msg_frame), tk.Label(self._msg_frame), tk.StringVar(), tk.StringVar()
        self._msg_hide = tk.Button(self._msg_frame)

        self._loading_pro = ttk.Progressbar(self._window)

    def __conf_font_size(self, n: int = 1):
        self._login_title_font_size = int(12 * n)
        self._login_btn_font_size = int(11 * n)
        self._win_ctrl_font_size = int(15 * n)
        self._menu_title_font_size = int(17 * n)
        self._program_title_font_size = int(14 * n)
        self._msg_font_size = int(20 * n)

    def __conf_tk(self, n: int = 1):
        self.__conf_win_ctrl_button()
        self.__conf_menu_title()
        self.__conf_menu(n)
        self.__conf_program_title()
        self.__conf_program(n)
        self.__conf_loading()
        self.__conf_msg()
        self.to_menu()  # 显示主页面
        self.to_program()

    def __conf_win_ctrl_button(self):
        title_font = make_font(size=self._win_ctrl_font_size)
        title_font_bold = make_font(size=self._win_ctrl_font_size, weight="bold")

        for bt in self._win_ctrl_button:
            bt: tk.Button
            bt['bg'] = conf.tk_btn_bg
            bt['font'] = title_font

        bt_main: tk.Button = self._win_ctrl_button[1]
        bt_main['text'] = 'Main'
        bt_main['font'] = title_font_bold
        bt_main['command'] = lambda: self.__to_main_menu()
        bt_main.place(relx=0.02, rely=0.86, relwidth=0.96, relheight=0.06)

        bt_back: tk.Button = self._win_ctrl_button[0]
        bt_back['text'] = 'back'
        bt_back['font'] = title_font_bold
        bt_back['state'] = 'disable'
        bt_back['command'] = lambda: self.__to_back_menu()
        bt_back.place(relx=0.02, rely=0.93, relwidth=0.96, relheight=0.06)

        rely = 0.02
        bt_help: tk.Button = self._win_ctrl_button[2]
        bt_help['text'] = 'Help'
        bt_help.place(relx=0.81, rely=rely, relwidth=0.05, relheight=0.05)

        bt_about: tk.Button = self._win_ctrl_button[3]
        bt_about['text'] = 'About'
        bt_about.place(relx=0.87, rely=rely, relwidth=0.05, relheight=0.05)

        bt_exit: tk.Button = self._win_ctrl_button[4]
        bt_exit['text'] = 'Exit'
        bt_exit['command'] = lambda: self.main_exit()
        bt_exit.place(relx=0.93, rely=rely, relwidth=0.05, relheight=0.05)

    def set_ctrl_back_button(self):
        if len(self._menu_list) <= 1:
            self._win_ctrl_button[0]['state'] = 'disable'
        else:
            self._win_ctrl_button[0]['state'] = 'normal'

    def __to_main_menu(self):
        self._menu_list = []
        self.to_menu()
        self.to_program()

    def __to_back_menu(self):
        assert len(self._menu_list) > 1
        self._menu_list.pop()  # 弹出最后一个元素
        self.to_menu(self._menu_list.pop())  # 再弹出一个元素

    def __conf_create_menu(self):
        frame_list = []

        for i in tk_menu.all_menu:
            frame_list.append(i(self, self._menu_back, conf.tk_win_bg))

        for i in frame_list:
            name, _ = i.get_menu_frame()
            self._menu_dict[name] = i

    def __conf_menu(self, n: int = 1):
        for i in self._menu_dict:
            menu = self._menu_dict[i]
            menu.conf_gui(conf.tk_btn_bg, n)

    def __conf_menu_title(self):
        self._menu_back['bg'] = conf.tk_win_bg
        self._menu_back['bd'] = 5
        self._menu_back['relief'] = "ridge"

        title_font = make_font(size=self._menu_title_font_size, weight="bold")
        self._menu_title[0]['bg'] = conf.tk_win_bg
        self._menu_title[0]['font'] = title_font
        self._menu_title[0]['textvariable'] = self._menu_title[1]

        self._menu_line['bg'] = '#000000'
        # 不立即显示

    def to_menu(self, name: str = "Main"):
        if self._menu_now is not None:
            self._menu_now[1].place_forget()

        menu = self._menu_dict.get(name)
        if menu is None:
            self.show_msg("Menu not found", f"System can not found menu:\n  {name}")
            return

        name, frame = menu.get_menu_frame()
        self._menu_title[1].set(name)

        self._menu_back.place(relx=0.02, rely=0.02, relwidth=0.20, relheight=0.96)
        self._menu_line.place(relx=0.06, rely=0.065, relwidth=0.88, height=1)  # 一个像素的高度即可
        self._menu_title[0].place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.03)
        frame.place(relx=0.02, rely=0.07, relwidth=0.96, relheight=0.79)

        self._menu_list.append(name)
        self._menu_now = name, frame, menu
        self.set_ctrl_back_button()

    def __conf_program_title(self):
        self._program_back['bg'] = conf.tk_win_bg
        self._program_back['relief'] = "ridge"
        self._program_back['bd'] = 5

        title_font = make_font(size=self._program_title_font_size, weight="bold")
        self._program_title[0]['bg'] = '#2468a2'
        self._program_title[0]['fg'] = "#F0F8FF"
        self._program_title[0]['font'] = title_font
        self._program_title[0]['anchor'] = 'w'
        self._program_title[0]['textvariable'] = self._program_title[1]
        # 不立即显示

    def __conf_create_program(self):
        program_list = []
        for i in tk_program.all_program:
            program_list.append(i(self, self._program_back, conf.tk_win_bg))

        for i in program_list:
            name, _ = i.get_program_frame()
            self._program_dict[name] = i

    def __conf_program(self, n: int = 1):
        for i in self._program_dict:
            program = self._program_dict[i]
            program.conf_gui(n)

    def to_program(self, name: str = "Welcome"):
        if self._program_now is not None:
            self._program_now[1].place_forget()

        program = self._program_dict.get(name)
        if program is None:
            self.show_msg("Program not found", f"System can not found program:\n  {name}")
            return

        name, frame = program.get_program_frame()

        self.__show_program()

        self._program_title[1].set(f' {name}')
        self._program_title[0].place(relx=0.00, rely=0.00, relwidth=1, relheight=0.05)

        frame.place(relx=0.02, rely=0.12, relwidth=0.96, relheight=0.86)

        self._program_now = name, frame, program

    def __show_program(self):
        self._program_back.place(relx=0.26, rely=0.1, relwidth=0.68, relheight=0.84)

    def __hide_program(self):
        self._program_back.place_forget()

    def __conf_loading(self):
        self._loading_pro['mode'] = 'indeterminate'
        self._loading_pro['orient'] = 'horizontal'
        self._loading_pro['maximum'] = 50

    def show_loading(self, _):
        self._is_loading = True
        self.set_all_btn_disable()
        self._loading_pro['value'] = 0
        self._loading_pro.place(relx=0.30, rely=0.035, relwidth=0.48, relheight=0.03)
        self._loading_pro.start(50)

    def stop_loading(self):
        self._is_loading = False
        self._loading_pro.place_forget()
        self._loading_pro.stop()
        self.set_reset_all_btn()

    def __conf_msg(self):
        title_font = make_font(size=self._msg_font_size + 1, weight="bold")
        info_font = make_font(size=self._msg_font_size - 1)

        self._msg_frame['bg'] = conf.tk_win_bg
        self._msg_frame['bd'] = 5
        self._msg_frame['relief'] = "ridge"
        # frame 不会立即显示

        self._msg_label[0]['font'] = title_font
        self._msg_label[0]['bg'] = conf.tk_win_bg
        self._msg_label[0]['anchor'] = 'w'
        self._msg_label[0]['textvariable'] = self._msg_label[2]

        self._msg_label[1]['font'] = info_font
        self._msg_label[1]['bg'] = conf.tk_win_bg
        self._msg_label[1]['anchor'] = 'nw'
        self._msg_label[1]['textvariable'] = self._msg_label[3]
        self._msg_label[1]['justify'] = 'left'

        self._msg_label[0].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.1)
        self._msg_label[1].place(relx=0.075, rely=0.2, relwidth=0.85, relheight=0.58)

        self._msg_hide['font'] = info_font
        self._msg_hide['text'] = 'close'
        self._msg_hide['bg'] = conf.tk_btn_bg
        self._msg_hide['command'] = lambda: self.hide_msg()
        self._msg_hide.place(relx=0.375, rely=0.80, relwidth=0.25, relheight=0.13)

    def show_msg(self, title, info, msg_type='info'):
        assert not self._is_loading  # loading 时不显示msg

        self.set_all_btn_disable()
        self._msg_label[2].set(f'{msg_type}: {title}')
        self._msg_label[3].set(f'{info}')

        frame_width = self._win_width * 0.50
        self._msg_label[1]['wraplength'] = frame_width * 0.85 - 5  # 设定自动换行的像素

        self._msg_frame.place(relx=0.30, rely=0.25, relwidth=0.55, relheight=0.50)
        # 不隐藏元素, 隐藏后界面会显得单调

    def hide_msg(self):
        self.set_reset_all_btn()
        self._msg_frame.place_forget()

    def set_all_btn_disable(self):
        for btn in self._win_ctrl_button[:-1]:  # Exit 不设置disable
            btn['state'] = 'disable'

        if self._menu_list != 0:
            menu = self._menu_dict.get(self._menu_list[-1], None)
            assert menu is not None
            menu.set_disable()

        if self._program_now is not None:
            self._program_now[2].set_disable()

    def set_reset_all_btn(self):
        for btn in self._win_ctrl_button[:-1]:
            btn['state'] = 'normal'

        self.set_ctrl_back_button()
        if self._menu_list != 0:
            menu = self._menu_dict.get(self._menu_list[-1], None)
            assert menu is not None
            menu.reset_disable()

        if self._program_now is not None:
            self._program_now[2].reset_disable()

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
        title_font = make_font(size=self._login_title_font_size, weight="bold")
        btn_font = make_font(size=self._login_btn_font_size, weight="bold")

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
        event = tk_event.LoginEvent(self).start(self._login_name[2].get(), self._login_passwd[2].get())
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

    def logout(self):
        super(AdminStation, self).logout()
        self.__show_login_window()

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

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()


if __name__ == '__main__':
    mysql_db = DB()
    station_ = AdminStation(mysql_db)
    station_.mainloop()
