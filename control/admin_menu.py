import abc
import tkinter as tk

from tool.type_ import *
from tool.tk import make_font, set_tk_disable_from_list

import admin


class AdminMenu(metaclass=abc.ABCMeta):
    def __init__(self, station: admin.AdminStationBase, win: Union[tk.Frame, tk.Toplevel, tk.Tk], color: str,
                 title: str):
        self.station = station
        self.win = win
        self.color = color
        self.frame = tk.Frame(self.win)
        self.frame['bg'] = color
        self.menu_title = title
        self.btn: List[tk.Button] = []
        self.btn_name: List[str] = []
        self.__conf_font()

    def __conf_font(self, n: int = 1):
        self.btn_font_size = int(16 * n)

    def set_disable(self):
        set_tk_disable_from_list(self.btn)

    def reset_disable(self):
        set_tk_disable_from_list(self.btn, flat='normal')

    def conf_gui(self, color: str, n: int = 1):
        self.__conf_font(n)

        btn_font = make_font(size=self.btn_font_size, weight="bold")
        height = 0.02
        for btn, text in zip(self.btn, self.btn_name):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = color
            btn.place(relx=0.02, rely=height, relwidth=0.96, relheight=0.1)
            height += 0.1 + 0.02

    def get_menu_frame(self) -> Tuple[str, tk.Frame]:
        return self.menu_title, self.frame


class MainMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Main")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["Creat", "Delete", "Search", "Update", "Logout"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.creat_command()
        self.btn[1]['command'] = lambda: self.delete_command()
        self.btn[2]['command'] = lambda: self.search_command()
        self.btn[3]['command'] = lambda: self.update_command()
        self.btn[4]['command'] = lambda: self.logout_command()

    def creat_command(self):
        self.station.to_menu("Creat")

    def delete_command(self):
        self.station.to_menu("Delete")

    def search_command(self):
        self.station.to_menu("Search")

    def update_command(self):
        self.station.to_menu("Update")

    def logout_command(self):
        self.station.logout()


class CreatMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Creat")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(4)]
        self.btn_name = ["NormalUser", "AutoNormalUser", "ManagerUser", "Garbage"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.creat_normal_user()
        self.btn[1]['command'] = lambda: self.creat_auto_user()
        self.btn[2]['command'] = lambda: self.creat_manager_user()
        self.btn[3]['command'] = lambda: self.creat_garbage()

    def creat_normal_user(self):
        self.station.to_program("CreatNormalUser")

    def creat_auto_user(self):
        self.station.to_program("CreatAutoNormalUser")

    def creat_manager_user(self):
        self.station.to_program("CreatManagerUser")

    def creat_garbage(self):
        self.station.to_program("CreatGarbage")


class DeleteMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Delete")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["User", "UserMore", "Garbage", "GarbageMore", "AllGarbage"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.del_user()
        self.btn[1]['command'] = lambda: self.del_users()
        self.btn[2]['command'] = lambda: self.del_garbage()
        self.btn[3]['command'] = lambda: self.del_garbage_more()
        self.btn[4]['command'] = lambda: self.del_all_garbage()

    def del_user(self):
        self.station.to_program("DeleteUser")

    def del_users(self):
        self.station.to_program("DeleteUsers")

    def del_garbage(self):
        self.station.to_program("DeleteGarbage")

    def del_garbage_more(self):
        self.station.to_program("DeleteGarbageMore")

    def del_all_garbage(self):
        self.station.to_program("DeleteAllGarbage")


class SearchMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Search")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(6)]
        self.btn_name = ["User", "UserAdvanced", "Garbage", "GarbageAdvanced", "Advanced", "Statistics"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.user_command()
        self.btn[1]['command'] = lambda: self.user_advanced_command()
        self.btn[2]['command'] = lambda: self.garbage_command()
        self.btn[3]['command'] = lambda: self.garbage_advanced_command()
        self.btn[4]['command'] = lambda: self.advanced_command()
        self.btn[5]['command'] = lambda: self.statistics_command()

    def user_command(self):
        self.station.to_program("SearchUser")

    def user_advanced_command(self):
        self.station.to_program("SearchUserAdvanced")

    def garbage_command(self):
        self.station.to_program("SearchGarbage")

    def garbage_advanced_command(self):
        self.station.to_program("SearchGarbageAdvanced")

    def advanced_command(self):
        self.station.to_program("SearchAdvanced")

    def statistics_command(self):
        self.station.to_menu("Statistics")


class UpdateMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Update")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(4)]
        self.btn_name = ["Score", "Reputation", "GarbageType", "GarbageCheck"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.update_score_command()
        self.btn[1]['command'] = lambda: self.update_reputation_command()
        self.btn[2]['command'] = lambda: self.update_garbage_type_command()
        self.btn[3]['command'] = lambda: self.update_garbage_result_command()

    def update_reputation_command(self):
        self.station.to_program("UpdateReputation")

    def update_score_command(self):
        self.station.to_program("UpdateScore")

    def update_garbage_type_command(self):
        self.station.to_program("UpdateGarbageType")

    def update_garbage_result_command(self):
        self.station.to_program("UpdateGarbageCheckResult")


class StatisticsMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "Statistics")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["Time", "Score", "Reputation", "BlackUser", "PassingRate"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)


all_menu = [MainMenu, CreatMenu, DeleteMenu, SearchMenu, UpdateMenu, StatisticsMenu]
