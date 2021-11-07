import abc
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk

from conf import Config
from core.garbage import GarbageBag
from core.user import User
from equipment.scan_garbage import write_gid_qr, write_all_gid_qr
from equipment.scan_user import write_uid_qr, write_all_uid_qr
from .event import TkEventMain
from sql.db import DB, search_from_garbage_checker_user
from sql.garbage import (create_new_garbage, search_garbage_by_fields, search_from_garbage_view,
                         del_garbage, del_garbage_not_use, del_garbage_wait_check, del_garbage_has_check,
                         del_garbage_where_scan_not_use, del_garbage_where_scan_wait_check,
                         del_garbage_where_scan_has_check,
                         del_garbage_where_not_use, del_garbage_where_wait_check, del_garbage_where_has_check,
                         del_all_garbage, del_all_garbage_scan,
                         update_garbage_check, update_garbage_type)

from sql.user import (create_new_user, del_user, del_user_from_where, del_user_from_where_scan,
                      search_user_by_fields, search_from_user_view,
                      update_user_score, update_user_reputation,
                      creat_user_from_csv, creat_auto_user_from_csv)
from tool.tk import make_font
from tool.typing import *


class AdminStationBase(TkEventMain, metaclass=abc.ABCMeta):
    """
    AdminStation基类
    封装管理员的相关操作
    主要是柯里化 sql相关函数
    """

    def __init__(self, db: DB):
        self._admin: Optional[User] = None
        self._db = db
        super(AdminStationBase, self).__init__()

    def get_db(self):
        return self._db

    def create_garbage(self, path: Optional[str], num: int = 1) -> List[tuple[str, Optional[GarbageBag]]]:
        re = []
        for _ in range(num):
            gar = create_new_garbage(self._db)
            assert gar
            if path is not None:
                res = write_gid_qr(gar.get_gid(), path, self._db)
                re.append(res)
            else:
                re.append(("", gar))
        return re

    def export_garbage_by_gid(self, path: Optional[str], gid: gid_t) -> Tuple[str, Optional[GarbageBag]]:
        return write_gid_qr(gid, path, self._db)

    def export_garbage(self, path: Optional[str], where: str) -> List[Tuple[str]]:
        return write_all_gid_qr(path, self._db, where=where)

    def create_user(self, name: uname_t, passwd: passwd_t, phone: str, manager: bool) -> Optional[User]:
        return create_new_user(name, passwd, phone, manager, self._db)

    def create_user_from_csv(self, path) -> List[User]:
        return creat_user_from_csv(path, self._db)

    def create_auto_user_from_csv(self, path) -> List[User]:
        return creat_auto_user_from_csv(path, self._db)

    def export_user_by_uid(self, path: str, uid: uid_t) -> Tuple[str, Optional[User]]:
        return write_uid_qr(uid, path, self._db)

    def export_user(self, path: str, where) -> List[str]:
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

    def search_garbage(self, columns, key_values: dict):
        return search_garbage_by_fields(columns, **key_values, db=self._db)

    def search_garbage_advanced(self, columns, sql):
        return search_from_garbage_view(columns, sql, self._db)

    def search_advanced(self, columns, sql):
        return search_from_garbage_checker_user(columns, sql, self._db)

    def update_user_score(self, score: score_t, where: str) -> int:
        return update_user_score(where, score, self._db)

    def update_user_reputation(self, reputation: score_t, where: str) -> int:
        return update_user_reputation(where, reputation, self._db)

    def update_garbage_type(self, type_: int, where: str):
        return update_garbage_type(where, type_, self._db)

    def update_garbage_check(self, check_: str, where: str):
        if check_ == 'pass':
            check = True
        elif check_ == 'fail':
            check = False
        else:
            return -1
        return update_garbage_check(where, check, self._db)

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
    def to_menu(self, name: str = "主页"):
        ...

    @abc.abstractmethod
    def to_program(self, name: str = "欢迎页"):
        ...

    @abc.abstractmethod
    def show_msg(self, title, info, msg_type='提示'):
        ...

    @abc.abstractmethod
    def show_warning(self, title, info):
        ...

    @abc.abstractmethod
    def hide_msg(self):
        ...


from . import admin_program as tk_program
from . import admin_menu as tk_menu
from . import admin_event as tk_event


class AdminStation(AdminStationBase):
    """
    AdminStation 管理员系统
    使用tkinter作为GUI
    构造与GarbageStation类似
    """

    def set_after_run(self, ms, func, *args):  # super.__init__可能会调用
        self.init_after_run_list.append((ms, func, args))

    def __conf_set_after_run(self):
        for ms, func, args in self.init_after_run_list:
            self._window.after(ms, func, *args)

    def set_after_run_now(self, ms, func, *args):
        self._window.after(ms, func, *args)

    def __init__(self, db: DB, refresh_delay: int = Config.tk_refresh_delay):
        self.init_after_run_list: List[Tuple[int, Callable, Tuple]] = []

        super().__init__(db)
        self.refresh_delay = refresh_delay

        self._window = tk.Tk()
        self.login_window = None
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))
        self._win_width = int(self._sys_width * (2 / 3))
        self.__conf_windows(before_load=True)

        self._full_screen = False
        self._is_loading = False
        self._disable_all_btn = False
        self._menu_now: Optional[Tuple[str, tk.Frame, tk_menu.AdminMenu]] = None
        self._program_now: Optional[Tuple[str, tk.Frame, tk_program.AdminProgram]] = None

        self.__conf_font_size()
        self.__conf_create_tk()
        self.__conf_create_menu()
        self.__conf_create_program()
        self.__conf_windows(before_load=False)
        self.__conf_tk()  # 在所有的Creat完成后才conf_tk
        # self.__show_login_window()  # 显示登录窗口, Debug期间暂时注释该代码

        self.__conf_set_after_run()

    def __conf_windows(self, before_load: bool = True):
        if before_load:
            self._window.title('HGSSystem: Manage Station')
            self._window.geometry(f'{self._win_width}x{self._win_height}')
            self._window['bg'] = Config.tk_win_bg
            self._window.resizable(False, False)
            self._window.protocol("WM_DELETE_WINDOW", lambda: self.main_exit())
            self._window.title('HGSSystem: Manage Station 加载中')
        else:
            self._window.title('HGSSystem: Manage Station')

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
        self._msg_line = tk.Label(self._msg_frame)
        self._msg_label = tk.Label(self._msg_frame), tk.Label(self._msg_frame), tk.StringVar(), tk.StringVar()
        self._msg_hide = tk.Button(self._msg_frame)

        self._loading_pro = ttk.Progressbar(self._window)

    def __conf_font_size(self, n: int = 1):
        self._login_title_font_size = int(12 * n)
        self._login_btn_font_size = int(12 * n)
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
            bt['bg'] = Config.tk_btn_bg
            bt['font'] = title_font

        bt_main: tk.Button = self._win_ctrl_button[1]
        bt_main['text'] = '主页'
        bt_main['font'] = title_font_bold
        bt_main['command'] = lambda: self.__to_main_menu()
        bt_main.place(relx=0.02, rely=0.86, relwidth=0.96, relheight=0.06)

        bt_back: tk.Button = self._win_ctrl_button[0]
        bt_back['text'] = '后退'
        bt_back['font'] = title_font_bold
        bt_back['state'] = 'disable'
        bt_back['command'] = lambda: self.__to_back_menu()
        bt_back.place(relx=0.02, rely=0.93, relwidth=0.96, relheight=0.06)

        rely = 0.02
        bt_help: tk.Button = self._win_ctrl_button[2]
        bt_help['text'] = '帮助'
        bt_help['command'] = lambda: self.to_program()
        bt_help.place(relx=0.81, rely=rely, relwidth=0.05, relheight=0.05)

        bt_about: tk.Button = self._win_ctrl_button[3]
        bt_about['text'] = '关于'
        bt_about['command'] = lambda: self.to_program("关于")
        bt_about.place(relx=0.87, rely=rely, relwidth=0.05, relheight=0.05)

        bt_exit: tk.Button = self._win_ctrl_button[4]
        bt_exit['text'] = '退出'
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

    def __to_back_menu(self):
        assert len(self._menu_list) > 1
        self._menu_list.pop()  # 弹出最后一个元素
        self.to_menu(self._menu_list.pop())  # 再弹出一个元素

    def __conf_create_menu(self):
        frame_list = []

        for i in tk_menu.all_menu:
            self._window.update()
            frame_list.append(i(self, self._menu_back, Config.tk_second_win_bg))

        for i in frame_list:
            name = i.get_menu_title()
            self._menu_dict[name] = i

    def __conf_menu(self, n: int = 1):
        for i in self._menu_dict:
            menu = self._menu_dict[i]
            menu.conf_gui(Config.tk_btn_bg, n)

    def __conf_menu_title(self):
        self._menu_back['bg'] = Config.tk_second_win_bg
        self._menu_back['bd'] = 5
        self._menu_back['relief'] = "ridge"

        title_font = make_font(size=self._menu_title_font_size, weight="bold")
        self._menu_title[0]['bg'] = Config.tk_second_win_bg
        self._menu_title[0]['font'] = title_font
        self._menu_title[0]['textvariable'] = self._menu_title[1]

        self._menu_line['bg'] = '#000000'
        # 不立即显示

    def to_menu(self, name: str = "主页"):
        if self._menu_now is not None:
            self._menu_now[1].place_forget()

        menu = self._menu_dict.get(name)
        if menu is None:
            self._menu_title[1].set(f'菜单错误')
            self.show_msg("菜单错误", f"系统无法找到菜单:\n  {name}")
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
        self._program_back['bg'] = Config.tk_second_win_bg
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
            self._window.update()
            program_list.append(i(self, self._program_back, Config.tk_second_win_bg))

        for i in program_list:
            name = i.get_title()
            self._program_dict[name] = i

    def __conf_program(self, n: int = 1):
        for i in self._program_dict:
            program = self._program_dict[i]
            program.conf_gui(n)

    def to_program(self, name: str = "欢迎页"):
        if self._program_now is not None:
            self._program_now[2].leave_program()
            self._program_now[1].place_forget()

        program = self._program_dict.get(name)
        if program is None:
            self._program_title[1].set(f' 程序加载错误')
            self.show_msg("程序错误", f"系统无法找到程序:\n  {name}")
            return

        program.to_program()
        name, frame = program.get_program_frame()

        self.__show_program()

        self._program_title[1].set(f' {name}')
        self._program_title[0].place(relx=0.00, rely=0.00, relwidth=1, relheight=0.05)

        frame.place(relx=0.02, rely=0.06, relwidth=0.96, relheight=0.92)

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

        self._msg_frame['bg'] = Config.tk_second_win_bg
        self._msg_frame['bd'] = 5
        self._msg_frame['relief'] = "ridge"
        # frame 不会立即显示

        self._msg_label[0]['font'] = title_font
        self._msg_label[0]['bg'] = Config.tk_second_win_bg
        self._msg_label[0]['anchor'] = 'w'
        self._msg_label[0]['textvariable'] = self._msg_label[2]

        self._msg_line['bg'] = '#000000'

        self._msg_label[1]['font'] = info_font
        self._msg_label[1]['bg'] = Config.tk_second_win_bg
        self._msg_label[1]['anchor'] = 'nw'
        self._msg_label[1]['textvariable'] = self._msg_label[3]
        self._msg_label[1]['justify'] = 'left'

        self._msg_label[0].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.1)
        self._msg_line.place(relx=0.05, rely=0.15, relwidth=0.9, height=1)  # 一个像素的高度即可
        self._msg_label[1].place(relx=0.075, rely=0.2, relwidth=0.85, relheight=0.58)

        self._msg_hide['font'] = info_font
        self._msg_hide['text'] = '关闭'
        self._msg_hide['bg'] = Config.tk_btn_bg
        self._msg_hide['command'] = lambda: self.hide_msg()
        self._msg_hide.place(relx=0.375, rely=0.80, relwidth=0.25, relheight=0.10)

    def show_msg(self, title, info, msg_type='提示'):
        assert not self._is_loading  # loading 时不显示msg

        self.set_all_btn_disable()
        self._msg_label[2].set(f'{msg_type}: {title}')
        self._msg_label[3].set(f'{info}')

        frame_width = self._win_width * 0.50
        self._msg_label[1]['wraplength'] = frame_width * 0.85 - 5  # 设定自动换行的像素

        self._msg_frame.place(relx=0.30, rely=0.25, relwidth=0.55, relheight=0.50)
        # 不隐藏元素, 隐藏后界面会显得单调

    def show_warning(self, title, info):
        self.show_msg(title, info, "警告")

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

        height = int(self._sys_height * (1 / 5))
        width = int(height * 2)

        if width > self._sys_width:
            width = int(self._sys_width * (2 / 3))
            height = int(width / 2)

        self.login_window.geometry(f'{width}x{height}')
        self.login_window['bg'] = Config.tk_win_bg
        self.login_window.resizable(False, False)
        self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.login_exit())
        self._login_frame = tk.Frame(self.login_window)
        self._login_name = [tk.Label(self._login_frame), tk.Entry(self._login_frame), tk.StringVar()]
        self._login_passwd = [tk.Label(self._login_frame), tk.Entry(self._login_frame), tk.StringVar()]
        self._login_btn = [tk.Button(self.login_window), tk.Button(self.login_window)]

        self.__conf_login_window()
        self.hide_main()
        self.login_window.deiconify()

    def __conf_login_window(self):
        title_font = make_font(size=self._login_title_font_size)
        btn_font = make_font(size=self._login_btn_font_size, weight="bold")

        self._login_frame['bg'] = "#EEE8AA"
        self._login_frame['bd'] = 5
        self._login_frame['relief'] = "ridge"
        self._login_frame.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.45)

        for lb, text in zip([self._login_name[0], self._login_passwd[0]], ["账户:", "密码:"]):
            lb['bg'] = "#EEE8AA"
            lb['font'] = title_font
            lb['text'] = text
            lb['anchor'] = 'e'

        for lb, var in zip([self._login_name[1], self._login_passwd[1]], [self._login_name[2], self._login_passwd[2]]):
            lb['font'] = title_font
            lb['textvariable'] = var

        self._login_name[0].place(relx=0.00, rely=0.13, relwidth=0.25, relheight=0.30)
        self._login_passwd[0].place(relx=0.00, rely=0.53, relwidth=0.25, relheight=0.30)

        self._login_name[1].place(relx=0.26, rely=0.13, relwidth=0.64, relheight=0.30)
        self._login_passwd[1]['show'] = "*"
        self._login_passwd[1].place(relx=0.26, rely=0.53, relwidth=0.64, relheight=0.30)

        self._login_btn[0]['bg'] = Config.tk_btn_bg
        self._login_btn[0]['font'] = btn_font
        self._login_btn[0]['text'] = '登录'
        self._login_btn[0]['command'] = lambda: self.login_call()
        self._login_btn[0].place(relx=0.54, rely=0.70, relwidth=0.16, relheight=0.15)

        self._login_btn[1]['bg'] = Config.tk_btn_bg
        self._login_btn[1]['font'] = btn_font
        self._login_btn[1]['text'] = '退出'
        self._login_btn[1]['command'] = lambda: self.login_exit()
        self._login_btn[1].place(relx=0.74, rely=0.70, relwidth=0.16, relheight=0.15)

    def login_call(self):
        event = tk_event.LoginEvent(self).start(self._login_name[2].get(), self._login_passwd[2].get())
        self.push_event(event)

    def login(self, user: User):
        if super(AdminStation, self).login(user):
            self.login_window.destroy()
            self.login_window = None
            self.show_main()
        else:
            msg.showerror("登录失败", "请重新尝试")
            self._login_name[2].set('')
            self._login_passwd[2].set('')

    def logout(self):
        if self._admin is not None:
            self._admin.destruct()
        super(AdminStation, self).logout()
        self.__show_login_window()

    def login_exit(self):
        if not msg.askokcancel('退出', '确定退出管理员系统吗？'):
            return
        if self.login_window is not None:
            self.login_window.destroy()
        self.exit_win()

    def main_exit(self):
        if not msg.askokcancel('退出', '确定退出管理员系统吗？'):
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
