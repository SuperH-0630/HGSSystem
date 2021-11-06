import abc
import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from math import ceil

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.axes import Axes
import numpy as np
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure

from tool.color import random_color
from tool.typing import *
from tool.tk import make_font, set_tk_disable_from_list
from tool.login import create_uid

from conf import Config
from . import admin
from . import admin_event as tk_event

from sql import DBBit
from sql.user import find_user_by_name
from core.garbage import GarbageType


class AdminProgram(metaclass=abc.ABCMeta):
    def __init__(self, station: "admin.AdminStation", win: Union[tk.Frame, tk.Toplevel, tk.Tk], color: str, title: str):
        self.station = station
        self.win = win
        self.color = color
        self.frame = tk.Frame(self.win)
        self.frame['bg'] = color
        self.program_title = title

    @abc.abstractmethod
    def set_disable(self):
        ...

    @abc.abstractmethod
    def reset_disable(self):
        ...

    @abc.abstractmethod
    def conf_gui(self, n: int = 1):
        ...

    def to_program(self):
        pass

    def leave_program(self):
        pass

    def get_title(self) -> str:
        return self.program_title

    def get_program_frame(self) -> Tuple[str, tk.Frame]:
        return self.program_title, self.frame


class WelcomeProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "欢迎页")

        self.title = tk.Label(self.frame)
        self.info = tk.Label(self.frame)
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(25 * n)
        self.info_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size, weight="bold")
        info_font = make_font(size=self.info_font_size)

        self.title['font'] = title_font
        self.title['bg'] = self.color
        self.title['text'] = '欢迎使用 HGSSystem 管理员系统\n[帮助]'

        self.info['bg'] = self.color
        self.info['font'] = info_font
        self.info['anchor'] = 'nw'
        self.info['justify'] = 'left'
        self.info['text'] = (f'''
HGSSystem 管理者界面:
  1) 点击菜单按钮进入子菜单或程序
  2) 创建 菜单包含创建类的程序
  3) 删除 菜单包含删除类的程序
  4) 搜索 菜单包含数据分析类的程序
  5) 更新 菜单包含数据更新类的程序
  6) 当离开操作系统时请退出登录以确保安全
  7) 只能使用具有管理员权限的账号登陆系统
  8) 只有admin用户可以完成危险操作(例如删除所有垃圾袋数据)

程序的运行:
  1) 在菜单中选中程序后，根据程序界面提示完成操作
  2) 操作过程通常会显示进度条，除非任务执行迅速
  3) 结果通常会被反馈, 且不会自动消失

系统登录:
  1) 仅Manager用户可以登录
                '''.strip())

        self.title.place(relx=0.1, rely=0.0, relwidth=0.8, relheight=0.2)
        self.info.place(relx=0.05, rely=0.21, relwidth=0.90, relheight=0.75)

    def set_disable(self):
        pass

    def reset_disable(self):
        pass


class AboutProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "关于")

        self.title = tk.Label(self.frame)
        self.info = tk.Label(self.frame)
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(25 * n)
        self.info_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size, weight="bold")
        info_font = make_font(size=self.info_font_size)

        self.title['font'] = title_font
        self.title['bg'] = self.color
        self.title['text'] = '关于 HGSSystem 管理员系统'

        self.info['bg'] = self.color
        self.info['font'] = info_font
        self.info['anchor'] = 'nw'
        self.info['justify'] = 'left'
        self.info['text'] = Config.about_info

        self.title.place(relx=0.1, rely=0.0, relwidth=0.8, relheight=0.2)
        self.info.place(relx=0.05, rely=0.21, relwidth=0.90, relheight=0.75)

    def set_disable(self):
        pass

    def reset_disable(self):
        pass


class CreateUserProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(3)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(3)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(3)]
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]

        self._conf("#FA8072", False)  # 默认颜色
        self.__conf_font()

    def _conf(self, bg_color, is_manager: bool):
        self.bg_color = bg_color
        self.is_manager = is_manager
        return self

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = self.bg_color
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.30)

        height = 0.1
        for lb, text, enter, var in zip(self.title, ["用户名:", "用户密码:", "手机号:"], self.enter, self.var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = self.bg_color
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.17)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.17)
            height += 0.30

        for btn, text, x, func in zip(self.btn,
                                      ["创建用户", "获取用户ID"],
                                      [0.2, 0.6],
                                      [lambda: self.create_by_name(), lambda: self.get_uid()]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func
            btn.place(relx=x, rely=0.7, relwidth=0.2, relheight=0.08)

    def __get_info(self) -> Optional[Tuple[uname_t, passwd_t, str]]:
        name: uname_t = self.var[0].get()
        passwd: passwd_t = self.var[1].get()
        phone: str = self.var[2].get()

        if len(name) == 0 or len(passwd) == 0 or len(phone) != 11:
            self.station.show_msg("用户创建失败", "请再次尝试, 输入用户名, 用户密码和11位手机号")
            return None

        return name, passwd, phone

    def create_by_name(self):
        res = self.__get_info()
        if res is None:
            return
        name, passwd, phone = res
        event = tk_event.CreateUserEvent(self.station).start(name, passwd, phone, self.is_manager)
        self.station.push_event(event)

    def get_uid(self):
        res = self.__get_info()
        if res is None:
            return
        name, passwd, phone = res
        uid = create_uid(name, passwd, phone)
        self.station.show_msg("获取用户ID", f"用户名: {name}\n用户ID: {uid}")

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        set_tk_disable_from_list(self.enter, flat='normal')


class CreateNormalUserProgram(CreateUserProgramBase):
    def __init__(self, station, win, color):
        super(CreateNormalUserProgram, self).__init__(station, win, color, "创建普通用户")


class CreateManagerUserProgram(CreateUserProgramBase):
    def __init__(self, station, win, color):
        super(CreateManagerUserProgram, self).__init__(station, win, color, "创建管理员")
        self._conf("#4b5cc4", True)


class CreateAutoNormalUserProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "创建自动用户")

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()
        self.btn: tk.Button = tk.Button(self.frame)  # create(生成用户) try(计算uid)

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#bce672"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.12)

        self.title['font'] = title_font
        self.title['text'] = "手机号:"
        self.title['bg'] = "#bce672"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.02, rely=0.25, relwidth=0.25, relheight=0.50)
        self.enter.place(relx=0.30, rely=0.25, relwidth=0.60, relheight=0.50)

        self.btn['font'] = btn_font
        self.btn['text'] = "创建用户"
        self.btn['bg'] = Config.tk_btn_bg
        self.btn['command'] = lambda: self.create_user()
        self.btn.place(relx=0.4, rely=0.7, relwidth=0.2, relheight=0.08)

    def create_user(self):
        phone = self.var.get()
        if len(phone) != 11:
            self.station.show_msg("UserInfoError", "Please, enter Phone(11)")
        event = tk_event.CreateUserEvent(self.station).start(None, None, phone, False)
        self.station.push_event(event)

    def set_disable(self):
        self.btn['state'] = 'disable'
        self.enter['state'] = 'disable'

    def reset_disable(self):
        self.btn['state'] = 'normal'
        self.enter['state'] = 'normal'


class CreateGarbageProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "创建垃圾袋")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame), tk.Label(self.enter_frame)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame), tk.Entry(self.enter_frame)]
        self.var: List[tk.Variable] = [tk.StringVar(), tk.StringVar()]
        self.create_btn: tk.Button = tk.Button(self.frame)
        self.file_btn: tk.Button = tk.Button(self.frame)

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#b69968"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.17)

        height = 0.1
        for lb, text, enter, var in zip(self.title, ["数量:", "导出位置:"], self.enter, self.var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#b69968"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)
            height += 0.43

        for btn, text, x, func in zip([self.create_btn, self.file_btn],
                                      ["创建垃圾袋", "选择目录"],
                                      [0.2, 0.6],
                                      [lambda: self.create_garbage(), lambda: self.choose_file()]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func
            btn.place(relx=x, rely=0.7, relwidth=0.2, relheight=0.08)

    def choose_file(self):
        path = askdirectory(title='选择二维码导出位置')
        self.var[1].set(path)

    def create_garbage(self):
        try:
            count = int(self.var[0].get())
            if count <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self.station.show_msg("类型错误", "数量必须为大于0的数字")
        else:
            path = self.var[1].get()
            if len(path) == 0:
                path = None
            event = tk_event.CreateGarbageEvent(self.station).start(path, count)
            self.station.push_event(event)

    def set_disable(self):
        self.create_btn['state'] = 'disable'
        self.file_btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.create_btn['state'] = 'normal'
        self.file_btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class ExportProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.gid_frame = tk.Frame(self.frame)
        self.gid_title: List[tk.Label] = [tk.Label(self.gid_frame), tk.Label(self.gid_frame)]
        self.gid_enter: List[tk.Entry] = [tk.Entry(self.gid_frame), tk.Entry(self.gid_frame)]
        self.gid_var: List[tk.Variable] = [tk.StringVar(), tk.StringVar()]

        self.where_frame = tk.Frame(self.frame)
        self.where_title: List[tk.Label] = [tk.Label(self.where_frame), tk.Label(self.where_frame)]
        self.where_enter: List[tk.Entry] = [tk.Entry(self.where_frame), tk.Entry(self.where_frame)]
        self.where_var: List[tk.Variable] = [tk.StringVar(), tk.StringVar()]

        self.create_btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]
        self.file_btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]

        self._conf("", [], [], [])
        self.__conf_font()

    def _conf(self, bg_color: str, title_id, title_where, title_command):
        self.bg_color = bg_color
        self.title_id = title_id
        self.title_where = title_where
        self.title_command = title_command

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.where_frame['bg'] = self.bg_color
        self.where_frame['bd'] = 5
        self.where_frame['relief'] = "ridge"
        self.where_frame.place(relx=0.2, rely=0.2, relwidth=0.6, relheight=0.17)

        self.gid_frame['bg'] = self.bg_color
        self.gid_frame['bd'] = 5
        self.gid_frame['relief'] = "ridge"
        self.gid_frame.place(relx=0.2, rely=0.6, relwidth=0.6, relheight=0.17)

        height = 0.1
        for lb, text, enter, var, lb_w, text_w, enter_w, var_w in zip(
                self.gid_title, self.title_id, self.gid_enter, self.gid_var,
                self.where_title, self.title_where, self.where_enter, self.where_var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = self.bg_color
            lb['anchor'] = 'e'

            lb_w['font'] = title_font
            lb_w['text'] = text_w
            lb_w['bg'] = self.bg_color
            lb_w['anchor'] = 'e'

            enter['textvariable'] = var
            enter['font'] = title_font

            enter_w['textvariable'] = var_w
            enter_w['font'] = title_font

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)

            lb_w.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter_w.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)

            height += 0.43

        for btn, text in zip(self.create_btn + self.file_btn, self.title_command):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg

        self.create_btn[1]['command'] = self.export_where
        self.create_btn[0]['command'] = self.export_id
        self.create_btn[1].place(relx=0.2, rely=0.39, relwidth=0.25, relheight=0.08)
        self.create_btn[0].place(relx=0.2, rely=0.79, relwidth=0.25, relheight=0.08)

        self.file_btn[1]['command'] = self.choose_file_where
        self.file_btn[0]['command'] = self.choose_file_id
        self.file_btn[1].place(relx=0.6, rely=0.39, relwidth=0.2, relheight=0.08)
        self.file_btn[0].place(relx=0.6, rely=0.79, relwidth=0.2, relheight=0.08)

    def choose_file_id(self):
        path = askdirectory(title='选择二维码导出位置')
        self.gid_var[1].set(path)

    def choose_file_where(self):
        path = askdirectory(title='选择二维码导出位置')
        self.where_var[1].set(path)

    def export_id(self):
        ...

    def export_where(self):
        ...

    def set_disable(self):
        set_tk_disable_from_list(self.gid_enter)
        set_tk_disable_from_list(self.create_btn)
        set_tk_disable_from_list(self.file_btn)

    def reset_disable(self):
        set_tk_disable_from_list(self.gid_enter, flat='normal')
        set_tk_disable_from_list(self.create_btn, flat='normal')
        set_tk_disable_from_list(self.file_btn, flat='normal')


class ExportGarbageProgram(ExportProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "导出垃圾袋二维码")
        self._conf("#afdfe4", ["垃圾袋ID:", "导出位置:"], ["条件:", "导出位置:"],
                   ["根据垃圾袋ID导出", "根据条件导出", "选择目录", "选择目录"])

    def export_id(self):
        gid = self.gid_var[0].get()
        path = self.gid_var[1].get()
        if len(path) == 0:
            self.station.show_warning("导出失败", "请指定导出的位置")
            return

        event = tk_event.ExportGarbageByIDEvent(self.station).start(path, gid)
        self.station.push_event(event)

    def export_where(self):
        where = self.where_var[0].get()
        path = self.where_var[1].get()
        if len(path) == 0:
            self.station.show_warning("导出失败", "请指定导出的位置")
            return

        event = tk_event.ExportGarbageAdvancedEvent(self.station).start(path, where)
        self.station.push_event(event)


class ExportUserProgram(ExportProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "导出用户二维码")
        self._conf("#f69c9f", ["用户ID:", "导出位置:"], ["条件:", "导出位置:"],
                   ["根据用户ID导出", "根据条件导出", "选择目录", "选择目录"])

    def export_id(self):
        uid = self.gid_var[0].get()
        path = self.gid_var[1].get()
        if len(path) == 0:
            self.station.show_warning("导出失败", "请指定导出的位置")
            return

        event = tk_event.ExportUserByIDEvent(self.station).start(path, uid)
        self.station.push_event(event)

    def export_where(self):
        where = self.where_var[0].get()
        path = self.where_var[1].get()
        if len(path) == 0:
            self.station.show_warning("导出失败", "请指定导出的位置")
            return

        event = tk_event.ExportUserAdvancedEvent(self.station).start(path, where)
        self.station.push_event(event)


class CreateUserFromCSVProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "从CSV导入用户")

        self.auto_frame = tk.Frame(self.frame)
        self.auto_title: tk.Label = tk.Label(self.auto_frame)
        self.auto_enter: tk.Entry = tk.Entry(self.auto_frame)
        self.auto_var: tk.Variable = tk.StringVar()

        self.enter_frame = tk.Frame(self.frame)
        self.path_title: tk.Label = tk.Label(self.enter_frame)
        self.path_enter: tk.Entry = tk.Entry(self.enter_frame)
        self.path_var: tk.Variable = tk.StringVar()

        self.create_btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]
        self.file_btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#EEE8AA"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.2, relwidth=0.6, relheight=0.12)

        self.auto_frame['bg'] = "#EEE8AA"
        self.auto_frame['bd'] = 5
        self.auto_frame['relief'] = "ridge"
        self.auto_frame.place(relx=0.2, rely=0.6, relwidth=0.6, relheight=0.12)

        self.auto_title['font'] = title_font
        self.auto_title['text'] = "CSV文件:"
        self.auto_title['bg'] = "#EEE8AA"
        self.auto_title['anchor'] = 'e'

        self.path_title['font'] = title_font
        self.path_title['text'] = "CSV文件:"
        self.path_title['bg'] = "#EEE8AA"
        self.path_title['anchor'] = 'e'

        self.auto_enter['textvariable'] = self.auto_var
        self.auto_enter['font'] = title_font

        self.path_enter['textvariable'] = self.path_var
        self.path_enter['font'] = title_font

        self.auto_title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.auto_enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        self.path_title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.path_enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text in zip(self.create_btn + self.file_btn,
                             ["创建用户", "创建自动用户", "选择CSV", "选择CSV"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg

        self.create_btn[0]['command'] = self.create
        self.create_btn[1]['command'] = self.create_auto
        self.create_btn[0].place(relx=0.2, rely=0.34, relwidth=0.25, relheight=0.08)
        self.create_btn[1].place(relx=0.2, rely=0.74, relwidth=0.25, relheight=0.08)

        self.file_btn[0]['command'] = self.choose_file
        self.file_btn[1]['command'] = self.choose_file_auto
        self.file_btn[0].place(relx=0.6, rely=0.34, relwidth=0.2, relheight=0.08)
        self.file_btn[1].place(relx=0.6, rely=0.74, relwidth=0.2, relheight=0.08)

    def choose_file_auto(self):
        path = askopenfilename(title='选择CSV文件', filetypes=[("CSV", ".csv")])
        self.auto_var.set(path)

    def choose_file(self):
        path = askopenfilename(title='选择CSV文件', filetypes=[("CSV", ".csv")])
        self.path_var.set(path)

    def create_auto(self):
        path = self.auto_var.get()
        event = tk_event.CreateAutoUserFromCSVEvent(self.station).start(path)
        self.station.push_event(event)

    def create(self):
        path = self.path_var.get()
        event = tk_event.CreateUserFromCSVEvent(self.station).start(path)
        self.station.push_event(event)

    def set_disable(self):
        self.auto_enter['state'] = 'disable'
        self.path_enter['state'] = 'disable'
        set_tk_disable_from_list(self.create_btn)
        set_tk_disable_from_list(self.file_btn)

    def reset_disable(self):
        self.auto_enter['state'] = 'normal'
        self.path_enter['state'] = 'normal'
        set_tk_disable_from_list(self.create_btn, flat='normal')
        set_tk_disable_from_list(self.file_btn, flat='normal')


class DeleteUserProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "删除用户")

        self.uid_frame = tk.Frame(self.frame)
        self.uid_title: tk.Label = tk.Label(self.uid_frame)
        self.uid_enter: tk.Entry = tk.Entry(self.uid_frame)
        self.uid_var: tk.Variable = tk.StringVar()

        self.name_frame = tk.Frame(self.frame)
        self.name_title: List[tk.Label] = [tk.Label(self.name_frame) for _ in range(2)]
        self.name_enter: List[tk.Entry] = [tk.Entry(self.name_frame) for _ in range(2)]
        self.name_var: List[tk.Variable] = [tk.StringVar() for _ in range(2)]

        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]  # uid-del, name-passwd-del

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.uid_frame['bg'] = "#FA8072"
        self.uid_frame['bd'] = 5
        self.uid_frame['relief'] = "ridge"
        self.uid_frame.place(relx=0.2, rely=0.20, relwidth=0.6, relheight=0.10)

        self.name_frame['bg'] = "#FA8072"
        self.name_frame['bd'] = 5
        self.name_frame['relief'] = "ridge"
        self.name_frame.place(relx=0.2, rely=0.48, relwidth=0.6, relheight=0.25)

        height = 0.17
        for lb, text, enter, var in zip(self.name_title, ["用户名:", "密码:"], self.name_enter, self.name_var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#FA8072"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.20)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.20)
            height += 0.45

        self.uid_title['font'] = title_font
        self.uid_title['text'] = "用户ID:"
        self.uid_title['bg'] = "#FA8072"
        self.uid_title['anchor'] = 'e'

        self.uid_enter['font'] = title_font
        self.uid_enter['textvariable'] = self.uid_var

        self.uid_title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.uid_enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text, func in zip(self.btn,
                                   ["通过用户ID删除", "通过用户名删除"],
                                   [lambda: self.del_by_uid(), lambda: self.del_by_name()]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func

        self.btn[0].place(relx=0.6, rely=0.32, relwidth=0.2, relheight=0.08)
        self.btn[1].place(relx=0.6, rely=0.75, relwidth=0.2, relheight=0.08)

    def del_by_uid(self):
        uid = self.uid_var.get()
        if len(uid) != 32:
            self.station.show_warning("用户ID错误", "用户ID必须为32位")
            return
        event = tk_event.DelUserEvent(self.station).start(uid)
        self.station.push_event(event)

    def del_by_name(self):
        name = self.name_var[0].get()
        passwd = self.name_var[1].get()
        if len(name) == 0 or len(passwd) == 0:
            self.station.show_warning("用户名或密码错误", "请输入用户名和密码")
            return
        uid = create_uid(name, passwd)
        event = tk_event.DelUserEvent(self.station).start(uid)
        self.station.push_event(event)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        set_tk_disable_from_list(self.name_enter)
        self.uid_enter['state'] = 'disable'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        set_tk_disable_from_list(self.name_enter, flat='normal')
        self.uid_enter['state'] = 'normal'


class DeleteUsersProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "删除多个用户")

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()

        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]  # del, scan

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#48c0a3"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.30, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['text'] = "条件:"
        self.title['anchor'] = 'e'
        self.title['bg'] = "#48c0a3"

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text, x, func in zip(self.btn,
                                      ["删除", "扫描"],
                                      [0.2, 0.6],
                                      [lambda: self.delete_user(), lambda: self.scan_user()]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func
            btn.place(relx=x, rely=0.6, relwidth=0.2, relheight=0.08)

    def delete_user(self):
        where = self.var.get()
        if len(where) == 0:
            self.station.show_warning("条件错误", "条件必须为正确的SQL语句")
            return
        event = tk_event.DelUserFromWhereEvent(self.station).start(where)
        self.station.push_event(event)

    def scan_user(self):
        where = self.var.get()
        if len(where) == 0:
            self.station.show_warning("条件错误", "条件必须为正确的SQL语句")
            return
        event = tk_event.DelUserFromWhereScanEvent(self.station).start(where)
        self.station.push_event(event)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'


class DeleteGarbageProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()

        self.int_var: tk.Variable = tk.IntVar()
        self.int_var.set(0)
        self.radio: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(4)]
        self.btn: tk.Button = tk.Button(self.frame)

        self.__conf_font()
        self._conf()

    def _conf(self, title: str = "垃圾袋ID:", color: str = "#b69968", support_del_all: bool = True):
        self.frame_title = title
        self.frame_color = color
        self.support_del_all = support_del_all

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = self.frame_color
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.30, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['text'] = self.frame_title
        self.title['bg'] = self.frame_color
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for i in range(4):
            radio = self.radio[i]
            radio['font'] = btn_font
            radio['text'] = ['均可', '仅未使用', '仅待检测', '仅已检测'][i]
            radio['bg'] = self.color
            radio['value'] = i
            radio['variable'] = self.int_var
            radio['anchor'] = 'w'

        if not self.support_del_all:
            self.int_var.set(1)
            self.radio[0]['state'] = 'disable'

        self.radio[0].place(relx=0.20, rely=0.43, relwidth=0.20, relheight=0.1)
        self.radio[1].place(relx=0.60, rely=0.43, relwidth=0.20, relheight=0.1)
        self.radio[2].place(relx=0.20, rely=0.55, relwidth=0.20, relheight=0.1)
        self.radio[3].place(relx=0.60, rely=0.55, relwidth=0.20, relheight=0.1)

        self.btn['font'] = btn_font
        self.btn['text'] = '删除'
        self.btn['bg'] = Config.tk_btn_bg
        self.btn['command'] = lambda: self.delete_garbage()
        self.btn.place(relx=0.4, rely=0.68, relwidth=0.2, relheight=0.08)

    def delete_garbage(self):
        ...

    def set_disable(self):
        self.enter['state'] = 'disable'
        self.btn['state'] = 'disable'

    def reset_disable(self):
        self.enter['state'] = 'normal'
        self.btn['state'] = 'normal'


class DeleteGarbageProgram(DeleteGarbageProgramBase):
    def __init__(self, station, win, color):
        super(DeleteGarbageProgram, self).__init__(station, win, color, "删除垃圾袋")

    def delete_garbage(self):
        where = self.int_var.get()
        assert where in [0, 1, 2, 3]

        gid = self.var.get()
        if len(gid) == 0:
            self.station.show_warning("垃圾袋ID错误", "请输入正确的垃圾袋ID")
            return

        event = tk_event.DelGarbageEvent(self.station).start(gid, where)
        self.station.push_event(event)


class DeleteGarbageMoreProgram(DeleteGarbageProgramBase):
    def __init__(self, station, win, color):
        super(DeleteGarbageMoreProgram, self).__init__(station, win, color, "删除多个垃圾袋")
        self.scan_btn = tk.Button(self.frame)
        self._conf("条件:", "#f58f98", False)

    def conf_gui(self, n: int = 1):
        super(DeleteGarbageMoreProgram, self).conf_gui(n)
        self.btn.place_forget()
        self.btn.place(relx=0.2, rely=0.68, relwidth=0.2, relheight=0.08)

        self.scan_btn['font'] = make_font(size=self.btn_font_size)
        self.scan_btn['text'] = '扫描'
        self.scan_btn['bg'] = Config.tk_btn_bg
        self.scan_btn['command'] = self.scan_garbage
        self.scan_btn.place(relx=0.6, rely=0.68, relwidth=0.2, relheight=0.08)

    def set_disable(self):
        super(DeleteGarbageMoreProgram, self).set_disable()
        self.scan_btn['state'] = 'disable'

    def reset_disable(self):
        super(DeleteGarbageMoreProgram, self).reset_disable()
        self.scan_btn['state'] = 'normal'

    def delete_garbage(self):
        where = self.int_var.get()
        assert where in [1, 2, 3]

        where_sql = self.var.get()
        if len(where_sql) == 0:
            self.station.show_warning("条件错误", "条件必须为正确的SQL语句")
            return

        event = tk_event.DelGarbageWhereEvent(self.station).start(where, where_sql)
        self.station.push_event(event)

    def scan_garbage(self):
        where = self.int_var.get()
        assert where in [1, 2, 3]

        where_sql = self.var.get()
        if len(where_sql) == 0:
            self.station.show_warning("条件错误", "条件必须为正确的SQL语句")
            return

        event = tk_event.DelGarbageWhereScanEvent(self.station).start(where, where_sql)
        self.station.push_event(event)


class DeleteAllGarbageProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "删除所有垃圾袋")

        self.dangerous: tk.Label = tk.Label(self.frame)

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()

        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]  # del, scan

        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.danger_font_size = int(20 * n)
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        danger_font = make_font(size=self.danger_font_size, weight="bold", underline=1)
        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)
        danger_btn_font = make_font(size=self.btn_font_size, weight="bold", overstrike=1)

        self.dangerous['bg'] = self.color
        self.dangerous['font'] = danger_font
        self.dangerous['fg'] = "#f20c00"
        self.dangerous['text'] = ("确定要从数据库删除所有垃圾袋吗?\n"
                                  "请输入[admin]用户的密码再继续操作.\n"
                                  "只有[admin]用户具有该操作的权限.\n"
                                  "这是相当危险的操作.\n"
                                  "操作后数据库可能无法恢复原数据.\n"
                                  "SuperHuan和程序的缔造者不会对\n"
                                  "此操作负责.\n"
                                  "删库跑路可不是一件好事.\n"
                                  "请遵守当地法律法规.")
        self.dangerous.place(relx=0.05, rely=0.03, relwidth=0.9, relheight=0.53)

        self.enter_frame['bg'] = "#f20c00"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.60, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['text'] = "密码:"
        self.title['bg'] = "#f20c00"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text, x in zip(self.btn, ["删除", "扫描"], [0.2, 0.6]):
            btn['text'] = text
            btn.place(relx=x, rely=0.78, relwidth=0.2, relheight=0.08)

        self.btn[0]['font'] = danger_btn_font
        self.btn[0]['bg'] = "#f20c00"
        self.btn[0]['command'] = lambda: self.delete_garbage()

        self.btn[1]['font'] = btn_font
        self.btn[1]['bg'] = Config.tk_btn_bg
        self.btn[1]['command'] = lambda: self.scan_garbage()

    def scan_garbage(self):
        event = tk_event.DelAllGarbageScanEvent(self.station)  # 不需要start
        self.station.push_event(event)

    def delete_garbage(self):
        passwd = self.var.get()
        if len(passwd) == 0:
            self.station.show_warning("密码错误", "请输入正确的[admin]用户密码")

        user = find_user_by_name('admin', passwd, self.station.get_db())
        if user is None or not user.is_manager():
            self.station.show_warning("密码错误", "请输入正确的[admin]用户密码")
            return

        event = tk_event.DelAllGarbageEvent(self.station)  # 不需要start
        self.station.push_event(event)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'


class SearchProgramBase(AdminProgram, metaclass=abc.ABCMeta):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)
        self.view_frame = tk.Frame(self.frame)
        self.view = ttk.Treeview(self.view_frame)
        self.y_scroll = tk.Scrollbar(self.view_frame)
        self.x_scroll = tk.Scrollbar(self.view_frame)

    def conf_view_gui(self, columns: list, relx, rely, relwidth, relheight,
                      x_scroll=0.05, y_scroll=0.02, color: str = "#FA8072"):
        self.view_frame['bg'] = color
        self.view_frame['bd'] = 2
        self.view_frame['relief'] = "ridge"
        self.view_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

        self.view['columns'] = columns
        self.view['show'] = 'headings'
        self.view['selectmode'] = 'none'

        for i in columns:
            self.view.column(i, anchor="c")
            self.view.heading(i, text=i)

        self.y_scroll['orient'] = 'vertical'
        self.y_scroll['command'] = self.view.yview
        self.view['yscrollcommand'] = self.y_scroll.set

        self.x_scroll['orient'] = 'horizontal'
        self.x_scroll['command'] = self.view.xview
        self.view['xscrollcommand'] = self.x_scroll.set

        self.view.place(relx=0.0, rely=0.0, relwidth=1 - y_scroll, relheight=1 - x_scroll)
        self.y_scroll.place(relx=0.98, rely=0.0, relwidth=y_scroll, relheight=1.0)
        self.x_scroll.place(relx=0.0, rely=1 - x_scroll, relwidth=1 - y_scroll, relheight=x_scroll)


class SearchUserProgram(SearchProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "搜索用户")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(3)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(3)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(3)]
        self.check: List[Tuple[tk.Checkbutton, tk.Variable]] = [(tk.Checkbutton(self.enter_frame), tk.IntVar())
                                                                for _ in range(3)]
        self.btn: tk.Button = tk.Button(self.frame)
        self._columns = ["UserID", "Name", "Phone", "Score", "Reputation", "IsManager"]
        self._columns_ch = ["用户ID[UserID]", "用户名[Name]", "手机号[Phone]",
                            "积分[Score]", "垃圾分类信用[Reputation]", "是否管理员[IsManager]"]
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#FA8072"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.0, relwidth=0.6, relheight=0.30)

        height = 0.1
        for lb, text, enter, var, check in zip(self.title,
                                               ["用户ID:", "用户名:", "手机号:"],
                                               self.enter, self.var, self.check):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#FA8072"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            check[0]['font'] = title_font
            check[0]['text'] = ''
            check[0]['bg'] = "#FA8072"
            check[0]['variable'] = check[1]
            check[1].set(1)

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.17)
            enter.place(relx=0.35, rely=height, relwidth=0.55, relheight=0.17)
            check[0].place(relx=0.92, rely=height, relwidth=0.04, relheight=0.17)
            height += 0.30

        self.btn['font'] = btn_font
        self.btn['text'] = "搜索"
        self.btn['bg'] = Config.tk_btn_bg
        self.btn['command'] = self.search_user
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        self.conf_view_gui(self._columns_ch, relx=0.05, rely=0.32, relwidth=0.9, relheight=0.55)

    def search_user(self):
        use_uid = self.check[0][1].get()
        use_name = self.check[1][1].get()
        use_phone = self.check[2][1].get()
        uid = None
        name = None
        phone = None
        if use_uid:
            uid = self.var[0].get()
            if len(uid) == 0:
                uid = None

        if use_name:
            name = self.var[1].get()
            if len(name) == 0:
                name = None

        if use_phone:
            phone = self.var[2].get()
            if len(phone) == 0:
                phone = None

        event = tk_event.SearchUserEvent(self.station).start(self._columns, uid, name, phone, self)
        self.station.push_event(event)

    def set_disable(self):
        self.btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class SearchAdvancedProgramBase(SearchProgramBase, metaclass=abc.ABCMeta):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()

        self.btn: tk.Button = tk.Button(self.frame)
        self._conf([], [], "#FA8072")  # 默认颜色
        self.__conf_font()

    def _conf(self, columns: list, columns_ch: list, bg_color):
        self.bg_color = bg_color
        self._columns = columns
        self._columns_ch = columns_ch
        return self

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = self.bg_color
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.00, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['bg'] = self.bg_color
        self.title['text'] = "条件:"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        self.btn['text'] = "搜索"
        self.btn['font'] = btn_font
        self.btn['bg'] = Config.tk_btn_bg
        self.btn['command'] = self.search
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        self.conf_view_gui(self._columns_ch, relx=0.05, rely=0.12, relwidth=0.9, relheight=0.76)

    def search(self):
        ...

    def set_disable(self):
        self.btn['state'] = 'disable'
        self.enter['state'] = 'disable'

    def reset_disable(self):
        self.btn['state'] = 'normal'
        self.enter['state'] = 'normal'


class SearchUserAdvancedProgram(SearchAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchUserAdvancedProgram, self).__init__(station, win, color, "高级搜索-用户")
        columns = ["UserID", "Name", "Phone", "Score", "Reputation", "IsManager"]
        columns_ch = ["用户ID[UserID]", "用户名[Name]", "手机号[Phone]",
                      "积分[Score]", "垃圾分类信用[Reputation]", "是否管理员[IsManager]"]
        self._conf(columns, columns_ch, '#48c0a3')

    def search(self):
        where = self.var.get()
        event = tk_event.SearchUserAdvancedEvent(self.station).start(self._columns, where, self)
        self.station.push_event(event)


class SearchGarbageProgram(SearchProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "搜索垃圾袋")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(8)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(8)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(8)]
        self.check: List[Tuple[tk.Checkbutton, tk.Variable]] = [(tk.Checkbutton(self.enter_frame), tk.IntVar())
                                                                for _ in range(8)]
        self._columns = ["GarbageID", "UserID", "CheckerID", "CreateTime", "UseTime", "Location", "GarbageType",
                         "CheckResult"]
        self._columns_zh = ["垃圾袋ID[GarbageID]", "使用者ID[UserID]", "检测者ID[CheckerID]", "创建时间[CreateTime]",
                            "使用时间[UseTime]", "使用地点[Location]", "垃圾类型[GarbageType]", "检测结果[CheckResult]"]
        self.btn: tk.Button = tk.Button(self.frame)
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.enter_frame['bg'] = "#7bbfea"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.0, relwidth=0.6, relheight=0.47)

        height = 0.02
        for lb, text, enter, var, check in zip(self.title,
                                               ["垃圾袋ID:", "使用者ID:", "检查者ID:", "创建时间:", "使用时间:",
                                                "使用地点:", "垃圾类型:", "检测结果:"],
                                               self.enter, self.var, self.check):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#7bbfea"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            check[0]['font'] = title_font
            check[0]['bg'] = "#7bbfea"
            check[0]['text'] = ''
            check[0]['variable'] = check[1]
            check[1].set(1)

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.10)
            enter.place(relx=0.35, rely=height, relwidth=0.55, relheight=0.10)
            check[0].place(relx=0.92, rely=height, relwidth=0.04, relheight=0.10)
            height += 0.121

        self.btn['font'] = btn_font
        self.btn['bg'] = Config.tk_btn_bg
        self.btn['text'] = "Search"
        self.btn['command'] = self.search_user
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        self.conf_view_gui(self._columns_zh, relx=0.05, rely=0.49, relwidth=0.9, relheight=0.38, x_scroll=0.07)

    def search_user(self):
        keys = ["gid", "uid", "cuid", "create_time", "use_time", "loc", "type_", "check"]
        key_values = {}
        for i, key in enumerate(keys):
            ck = self.check[i][1].get()
            if ck:
                res = self.enter[i].get()
                if len(res) > 0:
                    key_values[key] = res
                    continue
            key_values[key] = None

        event = tk_event.SearchGarbageEvent(self.station).start(self._columns, key_values, self)
        self.station.push_event(event)

    def set_disable(self):
        self.btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class SearchGarbageAdvancedProgram(SearchAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchGarbageAdvancedProgram, self).__init__(station, win, color, "高级搜索-垃圾袋")
        columns = ["GarbageID", "UserID", "CheckerID", "CreateTime", "UseTime", "Location", "GarbageType",
                   "CheckResult"]
        columns_zh = ["垃圾袋ID[GarbageID]", "使用者ID[UserID]", "检测者ID[CheckerID]", "创建时间[CreateTime]",
                      "使用时间[UseTime]", "使用地点[Location]", "垃圾类型[GarbageType]", "检测结果[CheckResult]"]
        self._conf(columns, columns_zh, '#d1923f')

    def search(self):
        where = self.var.get()
        event = tk_event.SearchGarbageAdvancedEvent(self.station).start(self._columns, where, self)
        self.station.push_event(event)


class SearchAdvancedProgram(SearchAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchAdvancedProgram, self).__init__(station, win, color, "高级搜索")
        columns = ["GarbageID", "UserID", "UserName", "UserPhone", "UserScore",
                   "UserReputation", "CheckerID", "CheckerName", "CheckerPhone",
                   "CreateTime", "UseTime", "Location", "GarbageType", "CheckResult"]
        columns_zh = ["垃圾袋ID[GarbageID]", "使用者ID[UserID]", "使用者名[UserName]", "使用者手机号[UserPhone]",
                      "使用者积分[UserScore]", "使用者垃圾分类信用[UserReputation]", "检测者ID[CheckerID]",
                      "检测这名[CheckerName]", "检测者手机号[CheckerPhone]", "创建时间[CreateTime]", "使用时间[UseTime]",
                      "使用地点[Location]", "垃圾类型[GarbageType]", "检测结果[CheckResult]"]
        self._conf(columns, columns_zh, '#426ab3')

    def search(self):
        where = self.var.get()
        event = tk_event.SearchAdvancedEvent(self.station).start(self._columns, where, self)
        self.station.push_event(event)


class UpdateUserProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(2)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(2)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(2)]

        self.where_frame = tk.Frame(self.frame)
        self.where_title: List[tk.Label] = [tk.Label(self.where_frame) for _ in range(2)]
        self.where_enter: List[tk.Entry] = [tk.Entry(self.where_frame) for _ in range(2)]
        self.where_var: List[tk.Variable] = [tk.StringVar() for _ in range(2)]

        self.btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]
        self._conf(["", ""], "#FA8072")
        self.__conf_font()

    def _conf(self, title: List[str], bg_color: str):
        self.bg_color = bg_color
        self.bg_color_where = bg_color
        self.enter_title = title

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.where_frame['bg'] = self.bg_color_where
        self.where_frame['bd'] = 5
        self.where_frame['relief'] = "ridge"
        self.where_frame.place(relx=0.2, rely=0.20, relwidth=0.6, relheight=0.17)

        self.enter_frame['bg'] = self.bg_color
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.58, relwidth=0.6, relheight=0.17)

        height = 0.1
        for lb, text, enter, var, lb_w, text_w, enter_w, var_w in (
                zip(self.title, self.enter_title, self.enter, self.var,
                    self.where_title, ["条件:", self.enter_title[1]], self.where_enter, self.where_var)):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = self.bg_color
            lb['anchor'] = 'e'

            lb_w['font'] = title_font
            lb_w['text'] = text_w
            lb_w['bg'] = self.bg_color_where
            lb_w['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            enter_w['font'] = title_font
            enter_w['textvariable'] = var_w

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)

            lb_w.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter_w.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)
            height += 0.43

        for btn, text, func in zip(self.btn,
                                   ["通过条件更新", "通过用户ID更新"],
                                   [self.update_by_where, self.update_by_uid]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func

        self.btn[0].place(relx=0.55, rely=0.40, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.78, relwidth=0.25, relheight=0.08)

    def update_by_uid(self):
        ...

    def update_by_where(self):
        ...

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        set_tk_disable_from_list(self.enter, flat='normal')


class UpdateUserScore(UpdateUserProgramBase):
    def __init__(self, station, win, color):
        super(UpdateUserScore, self).__init__(station, win, color, "更新用户-积分")
        self._conf(["用户ID:", "积分:"], "#afdfe4")

    def update_by_uid(self):
        uid = self.enter[0].get()
        score = int(self.enter[1].get())
        event = tk_event.UpdateUserScoreEvent(self.station).start(score, f"UserID='{uid}'")
        self.station.push_event(event)

    def update_by_where(self):
        where = self.where_enter[0].get()
        score = int(self.where_enter[1].get())
        event = tk_event.UpdateUserScoreEvent(self.station).start(score, where)
        self.station.push_event(event)


class UpdateUserReputation(UpdateUserProgramBase):
    def __init__(self, station, win, color):
        super(UpdateUserReputation, self).__init__(station, win, color, "更新用户-垃圾分类信用")
        self._conf(["用户ID:", "垃圾分类信用:"], "#f8aba6")

    def update_by_uid(self):
        uid = self.enter[0].get()
        reputation = int(self.enter[1].get())
        event = tk_event.UpdateUserReputationEvent(self.station).start(reputation, f"UserID='{uid}'")
        self.station.push_event(event)

    def update_by_where(self):
        where = self.where_enter[0].get()
        reputation = int(self.where_enter[1].get())
        event = tk_event.UpdateUserReputationEvent(self.station).start(reputation, where)
        self.station.push_event(event)


class UpdateGarbageTypeProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "更新垃圾袋-垃圾类型")

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.type: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(4)]
        self.var: List[tk.Variable] = [tk.StringVar, tk.IntVar()]

        self.where_frame = tk.Frame(self.frame)
        self.where_title: tk.Label = tk.Label(self.where_frame)
        self.where_enter: tk.Entry = tk.Entry(self.where_frame)
        self.where_type: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(4)]
        self.where_var: List[tk.Variable] = [tk.StringVar, tk.IntVar()]

        self.btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.where_frame['bg'] = "#fdb933"
        self.where_frame['bd'] = 5
        self.where_frame['relief'] = "ridge"
        self.where_frame.place(relx=0.2, rely=0.20, relwidth=0.6, relheight=0.10)

        self.enter_frame['bg'] = "#fdb933"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.60, relwidth=0.6, relheight=0.10)

        for lb, enter, radios, var, y, text in zip([self.title, self.where_title],
                                                   [self.enter, self.where_enter],
                                                   [self.type, self.where_type],
                                                   [self.var, self.where_var],
                                                   [0.32, 0.72],
                                                   ["垃圾袋ID:", "条件:"]):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#fdb933"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var[0]

            for i, radio in enumerate(radios):
                radio['font'] = btn_font
                radio['bg'] = self.color
                radio['text'] = GarbageType.GarbageTypeStrList_ch[i + 1]
                radio['value'] = i + 1
                radio['variable'] = var[1]
                radio['anchor'] = 'w'

            var[1].set(1)
            radios[0].place(relx=0.20, rely=y + 0.00, relwidth=0.20, relheight=0.04)
            radios[1].place(relx=0.60, rely=y + 0.00, relwidth=0.20, relheight=0.04)
            radios[2].place(relx=0.20, rely=y + 0.05, relwidth=0.20, relheight=0.04)
            radios[3].place(relx=0.60, rely=y + 0.05, relwidth=0.20, relheight=0.04)

            lb.place(relx=0.02, rely=0.2, relwidth=0.25, relheight=0.48)
            enter.place(relx=0.30, rely=0.2, relwidth=0.60, relheight=0.48)

        for btn, text, func in zip(self.btn,
                                   ["通过条件更新", "通过垃圾袋ID更新"],
                                   [self.update_by_where, self.update_by_gid]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn['command'] = func

        self.btn[0].place(relx=0.55, rely=0.43, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.83, relwidth=0.25, relheight=0.08)

    def update_by_gid(self):
        gid = self.enter.get()
        type_ = self.var[1].get()
        event = tk_event.UpdateGarbageTypeEvent(self.station).start(type_, f"GarbageID={gid}")
        self.station.push_event(event)

    def update_by_where(self):
        where = self.where_enter.get()
        type_ = self.where_var[1].get()
        event = tk_event.UpdateGarbageTypeEvent(self.station).start(type_, where)
        self.station.push_event(event)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'
        self.where_enter['state'] = 'normal'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'
        self.where_enter['state'] = 'normal'


class UpdateGarbageCheckResultProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "更新垃圾袋-检测结果")

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.type: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(2)]
        self.var: List[tk.Variable] = [tk.StringVar, tk.IntVar()]

        self.where_frame = tk.Frame(self.frame)
        self.where_title: tk.Label = tk.Label(self.where_frame)
        self.where_enter: tk.Entry = tk.Entry(self.where_frame)
        self.where_type: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(2)]
        self.where_var: List[tk.Variable] = [tk.StringVar, tk.IntVar()]

        self.btn: List[tk.Button] = [tk.Button(self.frame), tk.Button(self.frame)]
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(16 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size)
        btn_font = make_font(size=self.btn_font_size)

        self.where_frame['bg'] = "#abc88b"
        self.where_frame['bd'] = 5
        self.where_frame['relief'] = "ridge"
        self.where_frame.place(relx=0.2, rely=0.20, relwidth=0.6, relheight=0.10)

        self.enter_frame['bg'] = "#abc88b"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.60, relwidth=0.6, relheight=0.10)

        for lb, enter, radios, var, y, text in zip([self.title, self.where_title],
                                                   [self.enter, self.where_enter],
                                                   [self.type, self.where_type],
                                                   [self.var, self.where_var],
                                                   [0.32, 0.72],
                                                   ["垃圾袋ID:", "条件:"]):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#abc88b"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var[0]

            for i, radio in enumerate(radios):
                radio['font'] = btn_font
                radio['bg'] = self.color
                radio['text'] = ["投放错误", "投放正确"][i]
                radio['value'] = i
                radio['variable'] = var[1]
                radio['anchor'] = 'w'

            var[1].set(1)
            radios[0].place(relx=0.20, rely=y + 0.00, relwidth=0.20, relheight=0.04)
            radios[1].place(relx=0.60, rely=y + 0.00, relwidth=0.20, relheight=0.04)

            lb.place(relx=0.02, rely=0.2, relwidth=0.25, relheight=0.48)
            enter.place(relx=0.30, rely=0.2, relwidth=0.60, relheight=0.48)

        for btn, text, func in zip(self.btn,
                                   ["通过条件更新", "通过垃圾袋ID更新"],
                                   [self.update_by_where, self.update_by_gid]):
            btn['font'] = btn_font
            btn['bg'] = Config.tk_btn_bg
            btn['text'] = text
            btn['command'] = func

        self.btn[0].place(relx=0.55, rely=0.38, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.78, relwidth=0.25, relheight=0.08)

    def update_by_gid(self):
        gid = self.enter.get()
        check = (self.var[1].get() == 1)
        event = tk_event.UpdateGarbageCheckEvent(self.station).start(check, f"GarbageID={gid}")
        self.station.push_event(event)

    def update_by_where(self):
        where = self.where_enter.get()
        check = (self.where_var[1].get() == 1)
        event = tk_event.UpdateGarbageCheckEvent(self.station).start(check, where)
        self.station.push_event(event)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'
        self.where_enter['state'] = 'normal'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'
        self.where_enter['state'] = 'normal'


class StatisticsTimeProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.figure_frame = tk.Frame(self.frame)
        self.figure = Figure(dpi=100)
        self.plt_1: Axes = self.figure.add_subplot(211)  # 添加子图:2行1列第1个
        self.plt_2: Axes = self.figure.add_subplot(212, sharex=self.plt_1)  # 添加子图:2行1列第2个 (共享x轴)
        self.figure.subplots_adjust(hspace=0.7)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        self.canvas_tk = self.canvas.get_tk_widget()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.figure_frame)

        self.color_frame = tk.Frame(self.frame)
        self.show_list_tk = tk.Listbox(self.color_frame)
        self.show_list_scroll = tk.Scrollbar(self.color_frame)
        self.hide_list_tk = tk.Listbox(self.color_frame)
        self.hide_list_scroll = tk.Scrollbar(self.color_frame)

        self.btn_show = tk.Button(self.color_frame)
        self.btn_hide = tk.Button(self.color_frame)
        self.color_show_dict = {}
        self.color_hide_dict = {}
        self.export_lst = []

        self.export_btn = tk.Button(self.frame)
        self.refresh_btn = tk.Button(self.frame)
        self.reset_btn = tk.Button(self.frame)
        self.reverse_btn = tk.Button(self.frame)
        self.legend_show = tk.Checkbutton(self.frame), tk.IntVar()

        self._conf("#abc88b")
        self.__conf_font()

    def _conf(self, bg_color):
        self.bg_color = bg_color

    def __conf_font(self, n: int = 1):
        self.btn_font_size = int(14 * n)
        self.little_btn_font_size = int(12 * n)

    def to_program(self):
        self.refresh()

    def update_listbox(self):
        self.show_list_tk.delete(0, tk.END)  # 清空列表
        self.hide_list_tk.delete(0, tk.END)  # 清空列表
        for i in self.color_show_dict:
            self.show_list_tk.insert(tk.END, i)
            self.show_list_tk.itemconfig(tk.END,
                                         selectbackground=self.color_show_dict[i],
                                         bg=self.color_show_dict[i],
                                         selectforeground='#FFFFFF',
                                         fg='#000000')

        for i in self.color_hide_dict:
            self.hide_list_tk.insert(tk.END, i)
            self.hide_list_tk.itemconfig(tk.END,
                                         selectbackground=self.color_hide_dict[i],
                                         bg=self.color_hide_dict[i],
                                         selectforeground='#FFFFFF',
                                         fg='#000000')

    def check_show(self, res: str):
        color = self.color_show_dict.get(res)
        if color is not None:
            return color
        color = self.color_hide_dict.get(res)
        if color is not None:
            return None
        color = random_color()
        self.color_show_dict[res] = color
        return color

    def hide(self):
        i = self.show_list_tk.curselection()
        if len(i) == 0:
            return
        res = self.show_list_tk.get(i[0])
        self.hide_(res)
        self.update_listbox()

    def show(self):
        i = self.hide_list_tk.curselection()
        if len(i) == 0:
            return
        res = self.hide_list_tk.get(i[0])
        self.show_(res)
        self.update_listbox()

    def hide_(self, res):
        color = self.color_show_dict.get(res)
        if color is not None:
            del self.color_show_dict[res]
            self.color_hide_dict[res] = color

    def show_(self, res):
        color = self.color_hide_dict.get(res)
        if color is not None:
            del self.color_hide_dict[res]
            self.color_show_dict[res] = color

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)
        btn_font = make_font(size=self.btn_font_size)
        little_btn_font = make_font(size=self.little_btn_font_size)

        self.color_frame['bg'] = self.bg_color
        self.color_frame['bd'] = 5
        self.color_frame['relief'] = "ridge"

        self.show_list_tk.place(relx=0, rely=0, relwidth=0.90, relheight=0.475)
        self.show_list_scroll.place(relx=0.90, rely=0, relwidth=0.10, relheight=0.475)

        self.show_list_scroll['orient'] = 'vertical'
        self.show_list_scroll['command'] = self.show_list_tk.yview
        self.show_list_tk['yscrollcommand'] = self.show_list_scroll.set
        self.show_list_tk['activestyle'] = tk.NONE

        self.hide_list_tk.place(relx=0, rely=0.525, relwidth=0.90, relheight=0.475)
        self.hide_list_scroll.place(relx=0.90, rely=0.525, relwidth=0.10, relheight=0.475)

        self.hide_list_scroll['orient'] = 'vertical'
        self.hide_list_scroll['command'] = self.hide_list_tk.yview
        self.hide_list_tk['yscrollcommand'] = self.hide_list_scroll.set
        self.hide_list_tk['activestyle'] = tk.NONE

        for btn, text, func, x in zip([self.btn_show, self.btn_hide],
                                      ["显示", "隐藏"],
                                      [self.show, self.hide],
                                      [0.00, 0.50]):
            btn['font'] = little_btn_font
            btn['bg'] = Config.tk_btn_bg
            btn['text'] = text
            btn['command'] = func
            btn.place(relx=x, rely=0.475, relwidth=0.50, relheight=0.05)

        self.color_frame.place(relx=0.01, rely=0.02, relwidth=0.18, relheight=0.88)

        self.figure_frame['bg'] = self.bg_color
        self.figure_frame['bd'] = 5
        self.figure_frame['relief'] = "ridge"
        self.figure_frame.place(relx=0.21, rely=0.02, relwidth=0.79, relheight=0.88)

        self.canvas_tk.place(relx=0, rely=0, relwidth=1.0, relheight=0.9)
        self.toolbar.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

        for btn, text, func, x in zip([self.reset_btn, self.reverse_btn, self.refresh_btn, self.export_btn],
                                      ["复位选择", "反转选择", "刷新数据", "导出数据"],
                                      [self.reset, self.reverse, self.refresh, self.export],
                                      [0.37, 0.53, 0.69, 0.85]):
            btn['font'] = btn_font
            btn['bg'] = Config.tk_btn_bg
            btn['text'] = text
            btn['command'] = func
            btn.place(relx=x, rely=0.91, relwidth=0.15, relheight=0.08)

        self.legend_show[0]['font'] = btn_font
        self.legend_show[0]['bg'] = self.color
        self.legend_show[0]['text'] = "显示图例"
        self.legend_show[0]['variable'] = self.legend_show[1]
        self.legend_show[0].place(relx=0.21, rely=0.91, relwidth=0.15, relheight=0.08)

    def export(self, title, func: Callable):
        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write(f"Hour, Count, {title}\n")
            for i in self.export_lst:
                f.write(f"{i[0]}, {i[1]}, {func(i)}\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def refresh(self):
        self.plt_1.cla()
        self.plt_2.cla()

    def reset(self):
        self.color_show_dict.update(self.color_hide_dict)
        self.color_hide_dict = {}
        self.update_listbox()

    def reverse(self):
        tmp = self.color_show_dict
        self.color_show_dict = self.color_hide_dict
        self.color_hide_dict = tmp
        self.update_listbox()

    def show_result(self, res: Dict[str, any], lst: List):
        bottom = np.zeros(24)
        label_num = [i for i in range(24)]
        label_str = [f"{i}" for i in range(24)]
        res_type_lst: List = res['res_type']
        self.export_lst = lst
        max_y_plot = 1
        max_y_bar = 1
        for res_type in res_type_lst:
            res_count: Tuple[str] = res[res_type]
            if len(res_count) != 0:
                color = self.check_show(res_type)
                if color is None:
                    continue

                y = [0 for _ in range(24)]
                for i in res_count:
                    y[int(i[0])] += int(i[1])

                self.color_show_dict[res_type] = color
                self.plt_1.bar(label_num, y,
                               color=color,
                               align="center",
                               bottom=bottom,
                               tick_label=label_str,
                               label=res_type)
                self.plt_2.plot(label_num, y,
                                color=color,
                                label=res_type,
                                marker='o',
                                markersize=5)
                bottom += np.array(y)
                max_y_plot = max(max(y), max_y_plot)

        if self.legend_show[1].get() == 1:  # 显示图例
            self.plt_1.legend(loc="upper left")
            self.plt_2.legend(loc="upper left")

        self.plt_1.set_xlim(-1, 24)
        self.plt_1.set_xticks([i for i in range(0, 24, 2)])
        self.plt_1.set_xticklabels([f"{i}h" for i in range(0, 24, 2)])

        max_y_bar = int(max(bottom.max(), max_y_bar))
        self.plt_1.set_ylim(0, max_y_bar + max_y_bar * 0.1)
        step = ceil(max_y_bar / 5)  # 向上取整
        if step > 0:
            y_ticks = [i for i in range(0, max_y_bar, step)]
            y_ticklabels = [f'{i}' for i in range(0, max_y_bar, step)]
        else:
            y_ticks = []
            y_ticklabels = []
        y_ticks.append(max_y_bar)
        y_ticklabels.append(f"{max_y_bar}")
        self.plt_1.set_yticks(y_ticks)
        self.plt_1.set_yticklabels(y_ticklabels)  # 倒序

        self.plt_1.spines['right'].set_color('none')
        self.plt_1.spines['top'].set_color('none')
        self.plt_1.grid(axis='y')
        self.plt_1.set_title(f"{self.program_title}柱状图")

        self.plt_2.set_xlim(-1, 24)
        self.plt_2.set_xticks([i for i in range(0, 24, 2)])
        self.plt_2.set_xticklabels([f"{i}h" for i in range(0, 24, 2)])

        self.plt_2.set_ylim(0, max_y_plot + max_y_plot * 0.1)
        step = ceil(max_y_plot / 5)  # 向上取整
        if step > 0:
            y_ticks = [i for i in range(0, max_y_plot, step)]
            y_ticklabels = [f'{i}' for i in range(0, max_y_plot, step)]
        else:
            y_ticks = []
            y_ticklabels = []
        y_ticks.append(max_y_plot)
        y_ticklabels.append(f"{max_y_plot}")
        self.plt_2.set_yticks(y_ticks)
        self.plt_2.set_yticklabels(y_ticklabels)

        self.plt_2.spines['right'].set_color('none')
        self.plt_2.spines['top'].set_color('none')
        self.plt_2.grid(axis='y')
        self.plt_2.set_title(f"{self.program_title}折线图")

        self.canvas.draw()
        self.toolbar.update()
        self.update_listbox()

    def set_disable(self):
        self.export_btn['state'] = 'disable'
        self.reset_btn['state'] = 'disable'
        self.refresh_btn['state'] = 'disable'
        self.reverse_btn['state'] = 'disable'
        self.btn_show['state'] = 'disable'
        self.btn_hide['state'] = 'disable'

    def reset_disable(self):
        self.export_btn['state'] = 'normal'
        self.reset_btn['state'] = 'normal'
        self.refresh_btn['state'] = 'normal'
        self.reverse_btn['state'] = 'normal'
        self.btn_show['state'] = 'normal'
        self.btn_hide['state'] = 'normal'


class StatisticsTimeLocProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按投放区域")
        self._conf("#abc88b")

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["Location"], lambda i: i[2], self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Location", lambda i: i[2])


class StatisticsTimeTypeProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按投放类型")
        self._conf("#abc88b")
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[1]] = "#00BFFF"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[2]] = "#32CD32"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[3]] = "#DC143C"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[4]] = "#A9A9A9"

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["GarbageType"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Type", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data: bytes = i[2]
        return GarbageType.GarbageTypeStrList_ch[int(data.decode('utf-8'))]


class StatisticsTimeTypeLocProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按投放类型和区域")
        self._conf("#abc88b")

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["GarbageType", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Type-Location", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data: bytes = i[2]
        return f"{GarbageType.GarbageTypeStrList_ch[int(data.decode('utf-8'))]}-{i[3]}"


class StatisticsTimeCheckResultProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按检查结果")
        self._conf("#abc88b")
        self.color_show_dict['Pass'] = "#00BFFF"
        self.color_show_dict['Fail'] = "#DC143C"

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["CheckResult"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        if i[2] is None:
            return 'None'
        data: bytes = i[2]
        return 'Pass' if data == DBBit.BIT_1 else 'Fail'


class StatisticsTimeCheckResultAndTypeProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按检查结果和类型")
        self._conf("#abc88b")

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["CheckResult", "GarbageType"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result-Location", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data_1: bytes = i[2]
        data_2: bytes = i[3]
        if data_1 is None:
            tmp = 'None'
        elif data_1 == DBBit.BIT_1:
            tmp = 'Pass'
        else:
            tmp = 'Fail'
        return tmp + f'-{GarbageType.GarbageTypeStrList_ch[int(data_2.decode("utf-8"))]}'


class StatisticsTimeCheckResultAndLocProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-按检查结果和区域")
        self._conf("#abc88b")

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station).start(["CheckResult", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result-Type", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        if i[2] is None:
            return 'None'
        data_1: bytes = i[2]
        return (f'Pass' if data_1 == DBBit.BIT_1 else 'Fail') + f"-{i[3]}"


class StatisticsTimeDetailProgram(StatisticsTimeProgramBase):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "时段分析-详细分类")
        self._conf("#abc88b")

    def refresh(self):
        super().refresh()
        event = tk_event.CountTimeEvent(self.station)
        event.start(["CheckResult", "GarbageType", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Detail", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data_1: bytes = i[2]
        data_2: bytes = i[3]
        if data_1 is None:
            tmp = 'None'
        elif data_1 == DBBit.BIT_1:
            tmp = 'Pass'
        else:
            tmp = 'Fail'
        return tmp + f'-{GarbageType.GarbageTypeStrList_ch[int(data_2.decode("utf-8"))]}' + f'-{i[4]}'


class StatisticsUserBaseProgram(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.figure_frame = tk.Frame(self.frame)
        self.figure = Figure(dpi=100)
        self.plt: Axes = self.figure.add_subplot(111)  # 添加子图:1行1列第1个
        self.figure.subplots_adjust(bottom=0.2, top=0.93)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        self.canvas_tk = self.canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.figure_frame)
        self.color_bar: Optional[Colorbar] = None
        self.export_lst: Optional[np.array] = None

        self.export_btn = tk.Button(self.frame)
        self.refresh_btn = tk.Button(self.frame)
        self._conf("#abc88b")
        self.__conf_font()

    def _conf(self, bg_color):
        self.bg_color = bg_color

    def __conf_font(self, n: int = 1):
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)
        btn_font = make_font(size=self.btn_font_size)

        self.figure_frame['bg'] = self.bg_color
        self.figure_frame['bd'] = 5
        self.figure_frame['relief'] = "ridge"
        self.figure_frame.place(relx=0.00, rely=0.02, relwidth=1, relheight=0.88)

        self.canvas_tk.place(relx=0, rely=0, relwidth=1.0, relheight=0.9)
        self.toolbar.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

        for btn, text, func, x in zip([self.refresh_btn, self.export_btn],
                                      ["刷新数据", "导出数据"],
                                      [self.refresh, self.export],
                                      [0.34, 0.51]):
            btn['font'] = btn_font
            btn['bg'] = Config.tk_btn_bg
            btn['text'] = text
            btn['command'] = func
            btn.place(relx=x, rely=0.91, relwidth=0.15, relheight=0.08)

    def export(self):
        ...

    def refresh(self, event_class):
        self.plt.cla()
        if self.color_bar is not None:
            self.color_bar.remove()
        event = event_class(self.station).start(self)
        self.station.push_event(event)

    def set_disable(self):
        self.export_btn['state'] = 'disable'
        self.refresh_btn['state'] = 'disable'

    def reset_disable(self):
        self.export_btn['state'] = 'normal'
        self.refresh_btn['state'] = 'normal'


class StatisticsUserTinyProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsUserTinyProgram, self).__init__(station, win, color, "积分信用分析-细致")

    def show_result(self, lst: np.array):
        self.export_lst = lst
        x_label = [f'{i * 10}' for i in range(0, 51, 10)]
        y_label = [f'{i * 10}' for i in range(0, 101, 20)]

        im = self.plt.pcolormesh(lst, cmap='Blues')  # 用cmap设置配色方案

        self.plt.set_xticks(range(0, 101, 20))  # 设置x轴刻度
        self.plt.set_yticks(range(0, 101, 20))  # 设置y轴刻度
        self.plt.set_xticklabels(x_label)  # 设置x轴刻度标签
        self.plt.set_yticklabels(y_label)  # 设置y轴刻度标签
        self.plt.set_xlabel("用户积分")  # 设置x轴刻度标签
        self.plt.set_ylabel("垃圾分类信用")  # 设置y轴刻度标签

        self.color_bar = self.figure.colorbar(im, pad=0.03, ax=self.plt)  # 设置颜色条
        self.plt.set_title("积分信用分析-细致热图")  # 设置标题以及其位置和字体大小

        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        if self.export_lst is None:
            self.station.show_msg("保存数据", f"没有数据需要保存")
            return

        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write("#, " + ", ".join([f'[{i * 10} {i * 10 + 10}]' for i in range(0, 100, 1)]) + "\n")
            for i, lst in zip(range(0, 50, 1), self.export_lst):
                f.write(f"[{i * 10} {i * 10 + 10}], " + ", ".join([f"{a}" for a in lst]) + "\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        super().refresh(tk_event.CountScoreReputationTinyEvent)


class StatisticsUserLargeProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsUserLargeProgram, self).__init__(station, win, color, "积分信用分析-大致")

    def show_result(self, lst: np.array):
        self.export_lst = lst
        x_label = [f'{i * 10}' for i in range(0, 51, 10)]
        y_label = [f'{i * 10}' for i in range(0, 101, 20)]

        im = self.plt.pcolormesh(lst, cmap='Blues')  # 用cmap设置配色方案

        self.plt.set_xticks(range(0, 11, 2))  # 设置x轴刻度
        self.plt.set_yticks(range(0, 11, 2))  # 设置y轴刻度
        self.plt.set_xticklabels(x_label)  # 设置x轴刻度标签
        self.plt.set_yticklabels(y_label)  # 设置y轴刻度标签
        self.plt.set_xlabel("用户积分")  # 设置x轴刻度标签
        self.plt.set_ylabel("垃圾分类信用")  # 设置y轴刻度标签

        self.color_bar = self.figure.colorbar(im, pad=0.03, ax=self.plt)  # 设置颜色条
        self.plt.set_title("积分信用分析-大致热图")  # 设置标题以及其位置和字体大小

        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        if self.export_lst is None:
            self.station.show_msg("保存数据", f"没有数据需要保存")
            return

        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write("#, " + ", ".join([f'[{i * 10} {i * 10 + 100}]' for i in range(0, 100, 10)]) + "\n")
            for i, lst in zip(range(0, 50, 5), self.export_lst):
                f.write(f"[{i * 10} {i * 10 + 50}], " + ", ".join([f"{a}" for a in lst]) + "\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        super().refresh(tk_event.CountScoreReputationLargeEvent)


class StatisticsScoreDistributedProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsScoreDistributedProgram, self).__init__(station, win, color, "积分分布")

    def show_result(self, lst: np.array):
        bins = [i for i in range(0, 501, 10)]
        res = self.plt.hist(lst, bins)
        self.export_lst = res[0]

        self.plt.set_xlabel("用户积分")  # 设置x轴刻度标签
        self.plt.set_ylabel("分布")  # 设置x轴刻度标签
        self.plt.set_title("积分分布直方图")  # 设置标题以及其位置和字体大小
        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        if self.export_lst is None:
            self.station.show_msg("保存数据", f"没有数据需要保存")
            return

        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write("积分区间," + ", ".join([f'[{i * 10} {i * 10 + 100}]' for i in range(0, 501, 10)]) + "\n")
            f.write("积分分布," + ", ".join([f'{i}' for i in self.export_lst]) + "\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        self.plt.cla()
        if self.color_bar is not None:
            self.color_bar.remove()
        event = tk_event.ScoreReputationDistributedEvent(self.station).start("Score", self)
        self.station.push_event(event)


class StatisticsReputationDistributedProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsReputationDistributedProgram, self).__init__(station, win, color, "垃圾分类信用分布")

    def show_result(self, lst: np.array):
        bins = [i for i in range(0, 1001, 20)]
        res = self.plt.hist(lst, bins)
        self.export_lst = res[0]

        self.plt.set_xlabel("垃圾分类信用")  # 设置x轴刻度标签
        self.plt.set_ylabel("分布")  # 设置x轴刻度标签
        self.plt.set_title("垃圾分类信用分布直方图")  # 设置标题以及其位置和字体大小
        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        if self.export_lst is None:
            self.station.show_msg("保存数据", f"没有数据需要保存")
            return

        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write("信用区间," + ", ".join([f'[{i * 10} {i * 10 + 100}]' for i in range(0, 501, 10)]) + "\n")
            f.write("信用分布," + ", ".join([f'{i}' for i in self.export_lst]) + "\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        self.plt.cla()
        if self.color_bar is not None:
            self.color_bar.remove()
        event = tk_event.ScoreReputationDistributedEvent(self.station).start("Reputation", self)
        self.station.push_event(event)


class StatisticsPassRateGlobalProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsPassRateGlobalProgram, self).__init__(station, win, color, "通过率-全局")

    def show_result(self, lst: np.array):
        passing = float(lst[0][0])
        not_passing = 1 - passing
        data = [passing, not_passing]
        label = ["通过", "未通过"]

        res = self.plt.pie(data, radius=1, pctdistance=0.7, textprops=dict(color='w'),  # 不显示文字
                           startangle=45, autopct="%6.3f%%", wedgeprops=dict(width=0.6, edgecolor="w"))
        self.plt.legend(res[0], label, loc="lower left")
        self.plt.set_title("全局垃圾分类通过率")  # 设置标题以及其位置和字体大小

        self.plt.table(cellText=[data], cellLoc="center", colLabels=label,
                       rowLabels=['全局'], rowLoc='center', loc='bottom', colWidths=[0.4] * 2)

        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        self.station.show_msg("保存数据", f"数据不支持导出")
        return

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        self.plt.cla()
        event = tk_event.PassingRateEvent(self.station).start([], [], [], [], self)
        self.station.push_event(event)


class StatisticsPassRateTypeProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsPassRateTypeProgram, self).__init__(station, win, color, "通过率-按类型")

    def show_result(self, lst: List[Tuple[bytes, any]]):
        data_1, data_2, data_3, data_4 = [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]

        for i in lst:
            tmp: bytes = i[0]
            type_ = tmp.decode('utf-8')
            if type_ == '1':
                data_1 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '2':
                data_2 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '3':
                data_3 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '4':
                data_4 = [float(i[1]), 1 - float(i[1])]

        legend_text = []
        for data, r, s in zip([data_1, data_2, data_3, data_4], [0.3, 0.6, 0.9, 1.2], [0, 15, 30, 45]):
            res = self.plt.pie(data, radius=r, pctdistance=0.7,  # 不显示文字
                               startangle=s, autopct="%6.3f%%", wedgeprops=dict(width=0.3, edgecolor="w"))
            legend_text += res[0]

        label = []
        for i in GarbageType.GarbageTypeStrList_ch[1:]:
            label.append(f"{i}-通过")
            label.append(f"{i}-不通过")

        self.plt.table(cellText=[data_1, data_2, data_3, data_4], cellLoc="center", colLabels=['通过', '未通过'],
                       rowLabels=GarbageType.GarbageTypeStrList_ch[1:], rowLoc='center', loc='bottom')

        self.plt.legend(legend_text, label)
        self.plt.set_title("全局垃圾分类通过率")  # 设置标题以及其位置和字体大小
        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        self.station.show_msg("保存数据", f"数据不支持导出")
        return

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        self.plt.cla()
        event = tk_event.PassingRateEvent(self.station).start(["GarbageType"],
                                                              [],
                                                              ["g.GarbageType=garbage.GarbageType"],
                                                              ["GarbageType"], self)
        self.station.push_event(event)


class StatisticsPassRateLocProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsPassRateLocProgram, self).__init__(station, win, color, "通过率-按区域")
        self.loc_frame = tk.Frame(self.frame)
        self.loc_title = tk.Label(self.loc_frame)
        self.loc_enter = tk.Entry(self.loc_frame), tk.StringVar()

    def conf_gui(self, n: int = 1):
        super(StatisticsPassRateLocProgram, self).conf_gui(n)
        title_font = make_font(size=16)

        self.loc_frame['bg'] = self.bg_color
        self.loc_frame['bd'] = 5
        self.loc_frame['relief'] = "ridge"
        self.loc_frame.place(relx=0.0, rely=0.92, relwidth=0.33, relheight=0.07)

        self.loc_title['font'] = title_font
        self.loc_title['text'] = "区域:"
        self.loc_title['bg'] = self.bg_color
        self.loc_title['anchor'] = 'e'

        self.loc_enter[0]['font'] = title_font
        self.loc_enter[0]['textvariable'] = self.loc_enter[1]

        self.loc_title.place(relx=0.0, rely=0.02, relwidth=0.3, relheight=0.96)
        self.loc_enter[0].place(relx=0.3, rely=0.02, relwidth=0.7, relheight=0.96)

    def show_result(self, lst: np.array):
        passing = float(lst[0][0])

        label = ["通过", "未通过"]
        not_passing = 1 - passing
        data = [passing, not_passing]

        res = self.plt.pie(data, radius=1, pctdistance=0.7, textprops=dict(color='w'),  # 不显示文字
                           startangle=45, autopct="%6.3f%%", wedgeprops=dict(width=0.6, edgecolor="w"))
        self.plt.legend(res[0], label, loc="lower left")

        self.plt.table(cellText=[data], cellLoc="center", colLabels=label,
                       rowLabels=[f"区域"], rowLoc='center', loc='bottom')

        self.canvas.draw()
        self.toolbar.update()

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        where = self.loc_enter[1].get()
        if len(where) == 0:
            where = "全局"
            where_ = []
        else:
            where_ = [f"Location='{where}'"]

        self.plt.cla()
        self.plt.set_title(f"{where}垃圾分类通过率")  # 设置标题以及其位置和字体大小
        event = tk_event.PassingRateEvent(self.station).start([], where_, where_, [], self)
        self.station.push_event(event)


class StatisticsPassRateTypeAndLocProgram(StatisticsUserBaseProgram):
    def __init__(self, station, win, color):
        super(StatisticsPassRateTypeAndLocProgram, self).__init__(station, win, color, "通过率-按类型和区域")
        self.loc_frame = tk.Frame(self.frame)
        self.loc_title = tk.Label(self.loc_frame)
        self.loc_enter = tk.Entry(self.loc_frame), tk.StringVar()

    def conf_gui(self, n: int = 1):
        super(StatisticsPassRateTypeAndLocProgram, self).conf_gui(n)
        title_font = make_font(size=16)

        self.loc_frame['bg'] = self.bg_color
        self.loc_frame['relief'] = "ridge"
        self.loc_frame['bd'] = 5
        self.loc_frame.place(relx=0.0, rely=0.92, relwidth=0.33, relheight=0.07)

        self.loc_title['font'] = title_font
        self.loc_title['bg'] = self.bg_color
        self.loc_title['text'] = "区域:"
        self.loc_title['anchor'] = 'e'

        self.loc_enter[0]['font'] = title_font
        self.loc_enter[0]['textvariable'] = self.loc_enter[1]

        self.loc_title.place(relx=0.0, rely=0.02, relwidth=0.3, relheight=0.96)
        self.loc_enter[0].place(relx=0.3, rely=0.02, relwidth=0.7, relheight=0.96)

    def show_result(self, lst: List[Tuple[bytes, any]]):
        data_1, data_2, data_3, data_4 = [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]

        for i in lst:
            tmp: bytes = i[0]
            type_ = tmp.decode('utf-8')
            if type_ == '4':
                data_4 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '3':
                data_3 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '2':
                data_2 = [float(i[1]), 1 - float(i[1])]
            elif type_ == '1':
                data_1 = [float(i[1]), 1 - float(i[1])]

        legend_text = []
        for data, r, s in zip([data_1, data_2, data_3, data_4], [0.3, 0.6, 0.9, 1.2], [5, 20, 35, 50]):
            res = self.plt.pie(data, radius=r, pctdistance=0.7,  # 不显示文字
                               startangle=s, autopct="%6.3f%%", wedgeprops=dict(width=0.3, edgecolor="w"))
            legend_text += res[0]

        label = []
        for i in GarbageType.GarbageTypeStrList_ch[1:]:
            label.append(f"{i}-通过")
            label.append(f"{i}-不通过")

        self.plt.table(cellText=[data_1, data_2, data_3, data_4], cellLoc="center", colLabels=['通过', '未通过'],
                       rowLabels=GarbageType.GarbageTypeStrList_ch[1:], rowLoc='center', loc='bottom')

        self.plt.legend(legend_text, label)
        self.canvas.draw()
        self.toolbar.update()

    def export(self):
        self.station.show_msg("保存数据", f"数据不支持导出")
        return

    def to_program(self):
        self.refresh()

    def refresh(self, _=None):
        where = self.loc_enter[1].get()
        if len(where) == 0:
            where = "全局"
            where_ = []
        else:
            where_ = [f"Location='{where}'"]

        self.plt.cla()
        self.plt.set_title(f"{where}垃圾分类通过率")  # 设置标题以及其位置和字体大小
        event = tk_event.PassingRateEvent(self.station).start(["GarbageType"],
                                                              where_,
                                                              where_ + ["g.GarbageType=garbage.GarbageType"],
                                                              ["GarbageType"], self)
        self.station.push_event(event)


class StatisticsDateProgramBase(StatisticsTimeProgramBase):
    def _conf(self, bg_color, days: int = 7, days_sep: int = 1):
        super(StatisticsDateProgramBase, self)._conf(bg_color)
        self._days = days
        self._days_sep = days_sep

    def export(self, title, func: Callable):
        path = asksaveasfilename(title='选择CSV文件保存位置', filetypes=[("CSV", ".csv")])
        if not path.endswith(".csv"):
            path += ".csv"
        with open(path, "w") as f:
            f.write(f"Days, Count, {title}\n")
            for i in self.export_lst:
                f.write(f"{i[0]}, {i[1]}, {func(i)}\n")
        self.station.show_msg("保存数据", f"数据导出成功\n保存位置:\n  {path}")

    def show_result(self, res: Dict[str, any], lst: List, end_time: Optional[str] = None):
        if end_time is None:
            end_time = datetime.datetime.now()
        else:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        bottom = np.zeros(self._days)
        label_num = [i for i in range(self._days)]
        label_str = [f"{i}" for i in range(self._days)]

        res_type_lst: List = res['res_type']
        self.export_lst = lst
        max_y_plot = 1  # max_y的最大值
        max_y_bar = 1  # max_y的最大值
        for res_type in res_type_lst:
            res_count: List[Tuple[int, int, bytes]] = res[res_type]  # 距离今天的日期, 统计值, 分类值
            if len(res_count) != 0:
                color = self.check_show(res_type)
                if color is None:
                    continue

                y = [0 for _ in range(self._days)]
                for i in range(0, len(res_count)):  # 反向迭代列表
                    y[res_count[i][0]] = res_count[i][1]
                y = y[::-1]  # 反转列表, 使距离今天小的数据靠数据轴右侧
                max_y_plot = max(max(y), max_y_plot)
                self.color_show_dict[res_type] = color
                self.plt_1.plot(label_num, y,
                                color=color,
                                label=res_type,
                                marker='o',
                                markersize=5)
                self.plt_2.bar(label_num, y,
                               color=color,
                               align="center",
                               bottom=bottom,
                               tick_label=label_str,
                               label=res_type)
                bottom += np.array(y)

        if self.legend_show[1].get() == 1:  # 显示图例
            self.plt_1.legend(loc="upper left")
            self.plt_2.legend(loc="upper left")

        x_label = []
        for i in range(self._days - 1, -1, -self._days_sep):
            d = end_time - datetime.timedelta(days=i)
            x_label.append(d.strftime("%Y-%m-%d"))

        self.plt_1.set_xlim(-1, self._days)
        self.plt_1.set_xticks([i for i in range(0, self._days, self._days_sep)])
        self.plt_1.set_xticklabels(x_label, rotation=20)  # 倒序

        self.plt_1.set_ylim(0, max_y_plot + max_y_plot * 0.1)
        step = ceil(max_y_plot / 5)  # 向上取整
        if step > 0:
            y_ticks = [i for i in range(0, max_y_plot, step)]
            y_ticklabels = [f'{i}' for i in range(0, max_y_plot, step)]
        else:
            y_ticks = []
            y_ticklabels = []
        y_ticks.append(max_y_plot)
        y_ticklabels.append(f"{max_y_plot}")
        self.plt_1.set_yticks(y_ticks)
        self.plt_1.set_yticklabels(y_ticklabels)

        self.plt_1.spines['right'].set_color('none')
        self.plt_1.spines['top'].set_color('none')
        self.plt_1.grid(axis='y')
        self.plt_1.set_title(f"{self.program_title}折线图")

        self.plt_2.set_xlim(-1, self._days)
        self.plt_2.set_xticks([i for i in range(0, self._days, self._days_sep)])
        self.plt_2.set_xticklabels(x_label, rotation=20)

        max_y_bar = int(max(bottom.max(), max_y_bar))
        self.plt_2.set_ylim(0, max_y_bar + max_y_bar * 0.1)
        step = ceil(max_y_bar / 5)  # 向上取整
        if step > 0:
            y_ticks = [i for i in range(0, max_y_bar, step)]
            y_ticklabels = [f'{i}' for i in range(0, max_y_bar, step)]
        else:
            y_ticks = []
            y_ticklabels = []
        y_ticks.append(max_y_bar)
        y_ticklabels.append(f"{max_y_bar}")
        self.plt_2.set_yticks(y_ticks)
        self.plt_2.set_yticklabels(y_ticklabels)  # 倒序

        self.plt_2.spines['right'].set_color('none')
        self.plt_2.spines['top'].set_color('none')
        self.plt_2.grid(axis='y')
        self.plt_2.set_title(f"{self.program_title}柱状图")

        self.canvas.draw()
        self.toolbar.update()
        self.update_listbox()


class StatisticsDateTypeProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[1]] = "#00BFFF"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[2]] = "#32CD32"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[3]] = "#DC143C"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[4]] = "#A9A9A9"

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["GarbageType"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Type", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data: bytes = i[2]
        return GarbageType.GarbageTypeStrList_ch[int(data.decode('utf-8'))]


class StatisticsDateLocProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["Location"], lambda i: i[2], self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Location", lambda i: i[2])


class StatisticsDateTypeLocProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["GarbageType", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Type-Location", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data: bytes = i[2]
        return f"{GarbageType.GarbageTypeStrList_ch[int(data.decode('utf-8'))]}-{i[3]}"


class StatisticsDateCheckResultProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)
        self.color_show_dict['Pass'] = "#00BFFF"
        self.color_show_dict['Fail'] = "#DC143C"

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["CheckResult"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        if i[2] is None:
            return 'None'
        data: int = i[2]  # 返回garbage表时, BIT类型都是按bytes回传的, 但garbage_7和garbage_30会以int的方式回传
        return 'Pass' if data == 1 else 'Fail'


class StatisticsDateCheckResultAndTypeProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["CheckResult", "GarbageType"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result-Location", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data_1: int = i[2]
        data_2: bytes = i[3]
        if data_1 is None:
            tmp = 'None'
        elif data_1 == DBBit.BIT_1:
            tmp = 'Pass'
        else:
            tmp = 'Fail'
        return tmp + f'-{GarbageType.GarbageTypeStrList_ch[int(data_2.decode("utf-8"))]}'


class StatisticsDateCheckResultAndLocProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station).start(7, ["CheckResult", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Result-Type", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data_1: int = i[2]
        if data_1 is None:
            tmp = 'None'
        elif data_1 == DBBit.BIT_1:
            tmp = 'Pass'
        else:
            tmp = 'Fail'
        return tmp + f"-{i[3]}"


class StatisticsDateDetailProgram(StatisticsDateProgramBase):
    def __init__(self, station, win, color, title):
        super().__init__(station, win, color, title)
        self._conf("#abc88b", 7, 1)

    def refresh(self):
        super().refresh()
        event = tk_event.CountDateEvent(self.station)
        event.start(7, ["CheckResult", "GarbageType", "Location"], self.get_name, self)
        self.station.push_event(event)

    def export(self, *_, **__):
        super().export("Detail", self.get_name)

    @staticmethod
    def get_name(i: Tuple):
        data_1: int = i[2]
        data_2: bytes = i[3]
        if data_1 is None:
            tmp = 'None'
        elif data_1 == DBBit.BIT_1:
            tmp = 'Pass'
        else:
            tmp = 'Fail'
        return tmp + f'-{GarbageType.GarbageTypeStrList_ch[int(data_2.decode("utf-8"))]}' + f'-{i[4]}'


class StatisticsDate7TypeProgram(StatisticsDateTypeProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按投放类型")
        self._conf("#abc88b", 7, 1)
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[1]] = "#00BFFF"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[2]] = "#32CD32"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[3]] = "#DC143C"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[4]] = "#A9A9A9"


class StatisticsDate7LocProgram(StatisticsDateLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按投放区域")
        self._conf("#abc88b", 7, 1)


class StatisticsDate7TypeLocProgram(StatisticsDateTypeLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按投放类型和区域")
        self._conf("#abc88b", 7, 1)


class StatisticsDate7CheckResultProgram(StatisticsDateCheckResultProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按检查结果")
        self._conf("#abc88b", 7, 1)
        self.color_show_dict['Pass'] = "#00BFFF"
        self.color_show_dict['Fail'] = "#DC143C"


class StatisticsDate7CheckResultAndTypeProgram(StatisticsDateCheckResultAndTypeProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按检查结果和类型")
        self._conf("#abc88b", 7, 1)


class StatisticsDate7CheckResultAndLocProgram(StatisticsDateCheckResultAndLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-按检查结果和区域")
        self._conf("#abc88b", 7, 1)


class StatisticsDate7DetailProgram(StatisticsDateDetailProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近7日-详细分类")
        self._conf("#abc88b", 7, 1)


class StatisticsDate30TypeProgram(StatisticsDateTypeProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按投放类型")
        self._conf("#abc88b", 30, 5)
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[1]] = "#00BFFF"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[2]] = "#32CD32"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[3]] = "#DC143C"
        self.color_show_dict[GarbageType.GarbageTypeStrList_ch[4]] = "#A9A9A9"


class StatisticsDate30LocProgram(StatisticsDateLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按投放区域")
        self._conf("#abc88b", 30, 5)


class StatisticsDate30TypeLocProgram(StatisticsDateTypeLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按投放类型和区域")
        self._conf("#abc88b", 30, 5)


class StatisticsDate30CheckResultProgram(StatisticsDateCheckResultProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按检查结果")
        self._conf("#abc88b", 30, 5)
        self.color_show_dict['Pass'] = "#00BFFF"
        self.color_show_dict['Fail'] = "#DC143C"


class StatisticsDate30CheckResultAndTypeProgram(StatisticsDateCheckResultAndTypeProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按检查结果和类型")
        self._conf("#abc88b", 30, 5)


class StatisticsDate30CheckResultAndLocProgram(StatisticsDateCheckResultAndLocProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-按检查结果和区域")
        self._conf("#abc88b", 30, 5)


class StatisticsDate30DetailProgram(StatisticsDateDetailProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "最近30日-详细分类")
        self._conf("#abc88b", 30, 5)


all_program = [WelcomeProgram, CreateNormalUserProgram, CreateManagerUserProgram, CreateAutoNormalUserProgram,
               CreateGarbageProgram, DeleteUserProgram, DeleteUsersProgram, DeleteGarbageProgram,
               DeleteGarbageMoreProgram, DeleteAllGarbageProgram, SearchUserProgram, SearchUserAdvancedProgram,
               SearchGarbageProgram, SearchGarbageAdvancedProgram, SearchAdvancedProgram, UpdateUserScore,
               UpdateUserReputation, UpdateGarbageTypeProgram, UpdateGarbageCheckResultProgram,
               ExportGarbageProgram, ExportUserProgram, CreateUserFromCSVProgram, AboutProgram,
               StatisticsTimeLocProgram, StatisticsTimeTypeProgram, StatisticsTimeTypeLocProgram,
               StatisticsTimeCheckResultProgram, StatisticsTimeCheckResultAndTypeProgram,
               StatisticsTimeCheckResultAndLocProgram, StatisticsTimeDetailProgram, StatisticsUserTinyProgram,
               StatisticsUserLargeProgram, StatisticsScoreDistributedProgram, StatisticsReputationDistributedProgram,
               StatisticsPassRateGlobalProgram, StatisticsPassRateTypeProgram, StatisticsPassRateLocProgram,
               StatisticsPassRateTypeAndLocProgram, StatisticsDate7TypeProgram, StatisticsDate7LocProgram,
               StatisticsDate7TypeLocProgram, StatisticsDate7CheckResultProgram,
               StatisticsDate7CheckResultAndTypeProgram, StatisticsDate7CheckResultAndLocProgram,
               StatisticsDate7DetailProgram, StatisticsDate30TypeProgram, StatisticsDate30LocProgram,
               StatisticsDate30TypeLocProgram, StatisticsDate30CheckResultProgram,
               StatisticsDate30CheckResultAndTypeProgram, StatisticsDate30CheckResultAndLocProgram,
               StatisticsDate30DetailProgram]
