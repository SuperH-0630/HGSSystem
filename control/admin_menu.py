import abc
import tkinter as tk

from tool.type_ import *
from tool.tk import make_font, set_button_disable_from_list

import admin


class AdminMenu(metaclass=abc.ABCMeta):
    def __init__(self, station: admin.AdminStationBase, win: Union[tk.Frame, tk.Toplevel, tk.Tk], color: str):
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
    def conf_gui(self, color: str, n: int = 1):
        ...

    @abc.abstractmethod
    def get_menu_frame(self) -> Tuple[str, tk.Frame]:
        ...


class MainMenu(AdminMenu):
    def __init__(self, station, win, color):
        super(MainMenu, self).__init__(station, win, color)
        self.frame = tk.Frame(self.win)
        self.frame['bg'] = color

        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.btn_font_size = int(16 * n)

    def conf_gui(self, color: str, n: int = 1):
        self.__conf_font(n)

        btn_font = make_font(size=self.btn_font_size, weight="bold")
        height = 0.02
        for btn, text in zip(self.btn, ["Creat", "Delete", "Search", "Update", "Logout"]):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = color
            btn.place(relx=0.02, rely=height, relwidth=0.96, relheight=0.1)
            height += 0.1 + 0.02

    def get_menu_frame(self) -> Tuple[str, tk.Frame]:
        return "Main", self.frame

    def set_disable(self):
        set_button_disable_from_list(self.btn)

    def reset_disable(self):
        set_button_disable_from_list(self.btn, flat='normal')
