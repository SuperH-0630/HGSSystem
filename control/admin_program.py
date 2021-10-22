import abc
import tkinter as tk

from tool.type_ import *
from tool.tk import make_font, set_tk_disable_from_list

import conf
import admin
import admin_event as tk_event


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


all_program = [WelcomeProgram, CreatNormalUserProgram, CreatManagerUserProgram, CreatAutoNormalUserProgram,
               CreatGarbageProgram]
