import abc
import tkinter as tk

from tool.type_ import *
from tool.tk import make_font, set_button_disable_from_list

import admin
import admin_event as tk_event


class AdminProgram(metaclass=abc.ABCMeta):
    def __init__(self, station: admin.AdminStation, win: Union[tk.Frame, tk.Toplevel, tk.Tk], color: str):
        self.station = station
        self.win = win
        self.color = color

    @abc.abstractmethod
    def set_disable(self):
        ...

    @abc.abstractmethod
    def reset_disable(self):
        ...

    @abc.abstractmethod
    def conf_gui(self, n: int = 1):
        ...

    @abc.abstractmethod
    def get_program_frame(self) -> tk.Frame:
        ...


class WelcomeProgram(AdminProgram):
    def __init__(self, station, win, color):
        super(WelcomeProgram, self).__init__(station, win, color)
        self.frame = tk.Frame(self.win)
        self.frame['bg'] = color

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

    def get_program_frame(self) -> Tuple[str, tk.Frame]:
        return "Welcome", self.frame

    def set_disable(self):
        set_button_disable_from_list(self.btn)

    def reset_disable(self):
        set_button_disable_from_list(self.btn, flat='normal')
