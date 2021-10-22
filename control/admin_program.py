import abc
import tkinter as tk
import tkinter.ttk as ttk

from tool.type_ import *
from tool.tk import make_font, set_tk_disable_from_list

import conf
import admin
import admin_event as tk_event

from core.garbage import GarbageType


class AdminProgram(metaclass=abc.ABCMeta):
    def __init__(self, station: admin.AdminStation, win: Union[tk.Frame, tk.Toplevel, tk.Tk], color: str, title: str):
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

    def get_program_frame(self) -> Tuple[str, tk.Frame]:
        return self.program_title, self.frame


class WelcomeProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Welcome")

        self.title = tk.Label(self.frame)
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.title_font_size = int(25 * n)
        self.btn_font_size = int(14 * n)

    def conf_gui(self, n: int = 1):
        self.__conf_font(n)

        title_font = make_font(size=self.title_font_size, weight="bold")
        btn_font = make_font(size=self.btn_font_size)

        for btn, text in zip(self.btn, ["TestMSG", "TestProgress"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = '#d3d7d4'

        self.title['text'] = 'Welcome to HGSSystem Manager'
        self.title['font'] = title_font
        self.title['bg'] = self.color

        self.btn[0]['command'] = lambda: self.test_msg()
        self.btn[1]['command'] = lambda: self.test_progress()

        self.title.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.2)
        self.btn[0].place(relx=0.2, rely=0.7, relwidth=0.2, relheight=0.1)
        self.btn[1].place(relx=0.6, rely=0.7, relwidth=0.2, relheight=0.1)

    def test_progress(self):
        event = tk_event.TestProgressEvent(self.station)
        self.station.push_event(event)

    def test_msg(self):
        self.station.show_msg("Test Msg", "test msg")

    def set_disable(self):
        set_tk_disable_from_list(self.btn)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')


class CreatUserProgramBase(AdminProgram):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(3)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(3)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(3)]
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]  # creat(生成用户) try(计算uid)

        self._conf("#FA8072")  # 默认颜色
        self.__conf_font()

    def _conf(self, bg_color):
        self.bg_color = bg_color
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
        for lb, text, enter, var in zip(self.title, ["UserName:", "PassWord:", "Phone:"], self.enter, self.var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = self.bg_color
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.17)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.17)
            height += 0.30

        for btn, text, x in zip(self.btn, ["Creat", "GetUID"], [0.2, 0.6]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg
            btn.place(relx=x, rely=0.7, relwidth=0.2, relheight=0.08)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        set_tk_disable_from_list(self.enter, flat='normal')


class CreatNormalUserProgram(CreatUserProgramBase):
    def __init__(self, station, win, color):
        super(CreatNormalUserProgram, self).__init__(station, win, color, "CreatNormalUser")


class CreatManagerUserProgram(CreatUserProgramBase):
    def __init__(self, station, win, color):
        super(CreatManagerUserProgram, self).__init__(station, win, color, "CreatManagerUser")
        self._conf("#4b5cc4")


class CreatAutoNormalUserProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "CreatAutoNormalUser")

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()
        self.btn: tk.Button = tk.Button(self.frame)  # creat(生成用户) try(计算uid)

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
        self.enter_frame.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['text'] = "Phone:"
        self.title['bg'] = "#bce672"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.02, rely=0.2, relwidth=0.25, relheight=0.48)
        self.enter.place(relx=0.30, rely=0.2, relwidth=0.60, relheight=0.48)

        self.btn['font'] = btn_font
        self.btn['text'] = "Creat"
        self.btn['bg'] = conf.tk_btn_bg
        self.btn.place(relx=0.4, rely=0.7, relwidth=0.2, relheight=0.08)

    def set_disable(self):
        self.btn['state'] = 'disable'
        self.enter['state'] = 'disable'

    def reset_disable(self):
        self.btn['state'] = 'normal'
        self.enter['state'] = 'normal'


class CreatGarbageProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "CreatGarbage")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame), tk.Label(self.enter_frame)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame), tk.Entry(self.enter_frame)]
        self.var: List[tk.Variable] = [tk.StringVar(), tk.StringVar()]
        self.creat_btn: tk.Button = tk.Button(self.frame)
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
        for lb, text, enter, var in zip(self.title, ["Count:", "Export:"], self.enter, self.var):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#b69968"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.35)
            enter.place(relx=0.35, rely=height, relwidth=0.60, relheight=0.35)
            height += 0.43

        for btn, text, x in zip([self.creat_btn, self.file_btn], ["Creat", "ChoosePath"], [0.2, 0.6]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg
            btn.place(relx=x, rely=0.7, relwidth=0.2, relheight=0.08)

    def set_disable(self):
        self.creat_btn['state'] = 'disable'
        self.file_btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.creat_btn['state'] = 'normal'
        self.file_btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class DeleteUserProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "DeleteUser")

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
        for lb, text, enter, var in zip(self.name_title, ["UserName:", "PassWord:"], self.name_enter, self.name_var):
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
        self.uid_title['text'] = "UserID:"
        self.uid_title['bg'] = "#FA8072"
        self.uid_title['anchor'] = 'e'

        self.uid_enter['font'] = title_font
        self.uid_enter['textvariable'] = self.uid_var

        self.uid_title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.uid_enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text in zip(self.btn, ["Delete", "Delete"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg

        self.btn[0].place(relx=0.6, rely=0.32, relwidth=0.2, relheight=0.08)
        self.btn[1].place(relx=0.6, rely=0.75, relwidth=0.2, relheight=0.08)

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
        super().__init__(station, win, color, "DeleteUsers")

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
        self.title['text'] = "Where:"
        self.title['anchor'] = 'e'
        self.title['bg'] = "#48c0a3"

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text, x in zip(self.btn, ["Delete", "Scan"], [0.2, 0.6]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg
            btn.place(relx=x, rely=0.6, relwidth=0.2, relheight=0.08)

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
        self.radio: List[tk.Radiobutton] = [tk.Radiobutton(self.frame) for _ in range(4)]  # del, scan
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(2)]  # del, scan

        self.__conf_font()
        self._conf()

    def _conf(self, title: str = "GarbageID:", color: str = "#b69968"):
        self.frame_title = title
        self.frame_color = color

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
            radio['text'] = ['From-All', 'From-NotUse', 'From-Waiting', 'From-Used'][i]
            radio['bg'] = self.color
            radio['value'] = i
            radio['variable'] = self.int_var
            radio['anchor'] = 'w'

        self.radio[0].place(relx=0.20, rely=0.43, relwidth=0.20, relheight=0.1)
        self.radio[1].place(relx=0.60, rely=0.43, relwidth=0.20, relheight=0.1)
        self.radio[2].place(relx=0.20, rely=0.55, relwidth=0.20, relheight=0.1)
        self.radio[3].place(relx=0.60, rely=0.55, relwidth=0.20, relheight=0.1)

        for btn, text, x in zip(self.btn, ["Delete", "Scan"], [0.2, 0.6]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg
            btn.place(relx=x, rely=0.68, relwidth=0.2, relheight=0.08)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'


class DeleteAllGarbageProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "DeleteAllGarbage")

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
        self.dangerous['text'] = ("Delete all garbage from database?\n"
                                  "Please enter the admin-passwd to\n"
                                  "continue.\n"
                                  "Dangerous operation.\n"
                                  "The database may not be restored.\n"
                                  "SuperHuan is not responsible for\n"
                                  "the consequences.")
        self.dangerous.place(relx=0.05, rely=0.03, relwidth=0.9, relheight=0.43)

        self.enter_frame['bg'] = "#f20c00"
        self.enter_frame['bd'] = 5
        self.enter_frame['relief'] = "ridge"
        self.enter_frame.place(relx=0.2, rely=0.50, relwidth=0.6, relheight=0.10)

        self.title['font'] = title_font
        self.title['text'] = "Password:"
        self.title['bg'] = "#f20c00"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        for btn, text, x in zip(self.btn, ["Delete", "Scan"], [0.2, 0.6]):
            btn['text'] = text
            btn.place(relx=x, rely=0.68, relwidth=0.2, relheight=0.08)

        self.btn[0]['font'] = danger_btn_font
        self.btn[0]['bg'] = "#f20c00"
        self.btn[1]['font'] = btn_font
        self.btn[1]['bg'] = conf.tk_btn_bg

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'


class DeleteGarbageProgram(DeleteGarbageProgramBase):
    def __init__(self, station, win, color):
        super(DeleteGarbageProgram, self).__init__(station, win, color, "DeleteGarbage")


class DeleteGarbageMoreProgram(DeleteGarbageProgramBase):
    def __init__(self, station, win, color):
        super(DeleteGarbageMoreProgram, self).__init__(station, win, color, "DeleteGarbageMore")
        self._conf("Where:", "#f58f98")


class SearchBaseProgram(AdminProgram, metaclass=abc.ABCMeta):
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


class SearchUserProgram(SearchBaseProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "SearchUser")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(3)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(3)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(3)]
        self.check: List[Tuple[tk.Checkbutton, tk.Variable]] = [(tk.Checkbutton(self.enter_frame), tk.IntVar())
                                                                for _ in range(3)]
        self.btn: tk.Button = tk.Button(self.frame)
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
                                               ["UserID:", "UserName:", "Phone:"],
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
        self.btn['text'] = "Search"
        self.btn['bg'] = conf.tk_btn_bg
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        columns = ["UserID", "UserName", "Phone", "Score", "Reputation", "Rubbish"]
        self.conf_view_gui(columns, relx=0.05, rely=0.32, relwidth=0.9, relheight=0.55)

    def set_disable(self):
        self.btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class SearchUserAdvancedProgramBase(SearchBaseProgram, metaclass=abc.ABCMeta):
    def __init__(self, station, win, color, title: str):
        super().__init__(station, win, color, title)

        self.enter_frame = tk.Frame(self.frame)
        self.title: tk.Label = tk.Label(self.enter_frame)
        self.enter: tk.Entry = tk.Entry(self.enter_frame)
        self.var: tk.Variable = tk.StringVar()

        self.btn: tk.Button = tk.Button(self.frame)
        self._conf([], "#FA8072")  # 默认颜色
        self.__conf_font()

    def _conf(self, columns: list, bg_color):
        self.bg_color = bg_color
        self._columns = columns
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
        self.title['text'] = "Where:"
        self.title['anchor'] = 'e'

        self.enter['font'] = title_font
        self.enter['textvariable'] = self.var

        self.title.place(relx=0.01, rely=0.25, relwidth=0.30, relheight=0.50)
        self.enter.place(relx=0.35, rely=0.25, relwidth=0.60, relheight=0.50)

        self.btn['text'] = "Search"
        self.btn['font'] = btn_font
        self.btn['bg'] = conf.tk_btn_bg
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        self.conf_view_gui(self._columns, relx=0.05, rely=0.12, relwidth=0.9, relheight=0.76)

    def set_disable(self):
        self.btn['state'] = 'disable'
        self.enter['state'] = 'disable'

    def reset_disable(self):
        self.btn['state'] = 'normal'
        self.enter['state'] = 'normal'


class SearchUserAdvancedProgram(SearchUserAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchUserAdvancedProgram, self).__init__(station, win, color, "SearchUserAdvanced")
        columns = ["UserID", "UserName", "Phone", "Score", "Reputation", "Rubbish"]
        self._conf(columns, '#48c0a3')


class SearchGarbageProgram(SearchBaseProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "SearchGarbage")

        self.enter_frame = tk.Frame(self.frame)
        self.title: List[tk.Label] = [tk.Label(self.enter_frame) for _ in range(7)]
        self.enter: List[tk.Entry] = [tk.Entry(self.enter_frame) for _ in range(7)]
        self.var: List[tk.Variable] = [tk.StringVar() for _ in range(7)]
        self.check: List[Tuple[tk.Checkbutton, tk.Variable]] = [(tk.Checkbutton(self.enter_frame), tk.IntVar())
                                                                for _ in range(7)]
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
        self.enter_frame.place(relx=0.2, rely=0.0, relwidth=0.6, relheight=0.45)

        height = 0.02
        for lb, text, enter, var, check in zip(self.title,
                                               ["GarbageID:", "UserID:", "CheckerID:", "UseTime:",
                                                "Location:", "GarbageType:", "CheckResult:"],
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

            lb.place(relx=0.01, rely=height, relwidth=0.30, relheight=0.12)
            enter.place(relx=0.35, rely=height, relwidth=0.55, relheight=0.12)
            check[0].place(relx=0.92, rely=height, relwidth=0.04, relheight=0.12)
            height += 0.14

        self.btn['font'] = btn_font
        self.btn['bg'] = conf.tk_btn_bg
        self.btn['text'] = "Search"
        self.btn.place(relx=0.4, rely=0.9, relwidth=0.2, relheight=0.08)

        columns = ["GarbageID", "UserID", "CheckerID", "UseTime", "Location", "GarbageType", "CheckResult"]
        self.conf_view_gui(columns, relx=0.05, rely=0.47, relwidth=0.9, relheight=0.40, x_scroll=0.07)

    def set_disable(self):
        self.btn['state'] = 'disable'
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        self.btn['state'] = 'normal'
        set_tk_disable_from_list(self.enter, flat='normal')


class SearchGarbageAdvancedProgram(SearchUserAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchGarbageAdvancedProgram, self).__init__(station, win, color, "SearchGarbageAdvanced")
        columns = ["GarbageID", "UserID", "CheckerID", "UseTime", "Location", "GarbageType", "CheckResult"]
        self._conf(columns, '#d1923f')


class SearchAdvancedProgram(SearchUserAdvancedProgramBase):
    def __init__(self, station, win, color):
        super(SearchAdvancedProgram, self).__init__(station, win, color, "SearchAdvanced")
        columns = ["GarbageID", "UserID", "UserName", "Phone", "Score", "Reputation", "Rubbish",
                   "CheckerID", "CheckerName", "CheckerPhone", "UseTime", "Location", "GarbageType", "CheckResult"]
        self._conf(columns, '#426ab3')


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
                    self.where_title, ["Where:", self.enter_title[1]], self.where_enter, self.where_var)):
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

        for btn, text in zip(self.btn, ["Update Advanced", "Update By UserID"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg

        self.btn[0].place(relx=0.55, rely=0.40, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.78, relwidth=0.25, relheight=0.08)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        set_tk_disable_from_list(self.enter)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        set_tk_disable_from_list(self.enter, flat='normal')


class UpdateUserScoreBase(UpdateUserProgramBase):
    def __init__(self, station, win, color):
        super(UpdateUserScoreBase, self).__init__(station, win, color, "UpdateScore")
        self._conf(["UserID:", "Score:"], "#afdfe4")


class UpdateUserReputationBase(UpdateUserProgramBase):
    def __init__(self, station, win, color):
        super(UpdateUserReputationBase, self).__init__(station, win, color, "UpdateReputation")
        self._conf(["UserID:", "Reputation:"], "#f8aba6")


class UpdateGarbageTypeProgram(AdminProgram):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "UpdateGarbageType")

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
                                                   ["GarbageID:", "Where:"]):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#fdb933"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var[0]

            for i, radio in enumerate(radios):
                radio['font'] = btn_font
                radio['bg'] = self.color
                radio['text'] = GarbageType.GarbageTypeStrList[i + 1]
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

        for btn, text in zip(self.btn, ["Update Advanced", "Update By GarbageID"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = conf.tk_btn_bg

        self.btn[0].place(relx=0.55, rely=0.43, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.83, relwidth=0.25, relheight=0.08)

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
        super().__init__(station, win, color, "UpdateGarbageCheckResult")

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
                                                   ["GarbageID:", "Where:"]):
            lb['font'] = title_font
            lb['text'] = text
            lb['bg'] = "#abc88b"
            lb['anchor'] = 'e'

            enter['font'] = title_font
            enter['textvariable'] = var[0]

            for i, radio in enumerate(radios):
                radio['font'] = btn_font
                radio['bg'] = self.color
                radio['text'] = ["Fail", "Pass"][i]
                radio['value'] = i
                radio['variable'] = var[1]
                radio['anchor'] = 'w'

            var[1].set(1)
            radios[0].place(relx=0.20, rely=y + 0.00, relwidth=0.20, relheight=0.04)
            radios[1].place(relx=0.60, rely=y + 0.00, relwidth=0.20, relheight=0.04)

            lb.place(relx=0.02, rely=0.2, relwidth=0.25, relheight=0.48)
            enter.place(relx=0.30, rely=0.2, relwidth=0.60, relheight=0.48)

        for btn, text in zip(self.btn, ["Update Advanced", "Update By GarbageID"]):
            btn['font'] = btn_font
            btn['bg'] = conf.tk_btn_bg
            btn['text'] = text

        self.btn[0].place(relx=0.55, rely=0.38, relwidth=0.25, relheight=0.08)
        self.btn[1].place(relx=0.55, rely=0.78, relwidth=0.25, relheight=0.08)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)
        self.enter['state'] = 'disable'
        self.where_enter['state'] = 'normal'

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')
        self.enter['state'] = 'normal'
        self.where_enter['state'] = 'normal'


all_program = [WelcomeProgram, CreatNormalUserProgram, CreatManagerUserProgram, CreatAutoNormalUserProgram,
               CreatGarbageProgram, DeleteUserProgram, DeleteUsersProgram, DeleteGarbageProgram,
               DeleteGarbageMoreProgram, DeleteAllGarbageProgram, SearchUserProgram, SearchUserAdvancedProgram,
               SearchGarbageProgram, SearchGarbageAdvancedProgram, SearchAdvancedProgram, UpdateUserScoreBase,
               UpdateUserReputationBase, UpdateGarbageTypeProgram, UpdateGarbageCheckResultProgram]
