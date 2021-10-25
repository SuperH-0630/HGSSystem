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
        super().__init__(station, win, color, "主页")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["创建", "删除", "搜索", "更新", "退出登录"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.create_command()
        self.btn[1]['command'] = lambda: self.delete_command()
        self.btn[2]['command'] = lambda: self.search_command()
        self.btn[3]['command'] = lambda: self.update_command()
        self.btn[4]['command'] = lambda: self.logout_command()

    def create_command(self):
        self.station.to_menu("创建")

    def delete_command(self):
        self.station.to_menu("删除")

    def search_command(self):
        self.station.to_menu("搜索")

    def update_command(self):
        self.station.to_menu("更新")

    def logout_command(self):
        self.station.logout()


class CreateMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "创建")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(7)]
        self.btn_name = ["普通用户", "自动创建", "管理员用户", "垃圾袋",
                         "导出用户二维码", "导出垃圾袋二维码", "从CSV导入用户"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.create_normal_user()
        self.btn[1]['command'] = lambda: self.create_auto_user()
        self.btn[2]['command'] = lambda: self.create_manager_user()
        self.btn[3]['command'] = lambda: self.create_garbage()
        self.btn[4]['command'] = lambda: self.export_user()
        self.btn[5]['command'] = lambda: self.export_garbage()
        self.btn[6]['command'] = lambda: self.create_user_from_csv()

    def create_normal_user(self):
        self.station.to_program("创建普通用户")

    def create_auto_user(self):
        self.station.to_program("创建自动用户")

    def create_manager_user(self):
        self.station.to_program("创建管理员")

    def create_garbage(self):
        self.station.to_program("创建垃圾袋")

    def export_user(self):
        self.station.to_program("导出用户二维码")

    def export_garbage(self):
        self.station.to_program("导出垃圾袋二维码")

    def create_user_from_csv(self):
        self.station.to_program("从CSV导入用户")


class DeleteMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "删除")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["用户", "多个用户", "垃圾袋", "多个垃圾袋", "所有垃圾袋"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.del_user()
        self.btn[1]['command'] = lambda: self.del_users()
        self.btn[2]['command'] = lambda: self.del_garbage()
        self.btn[3]['command'] = lambda: self.del_garbage_more()
        self.btn[4]['command'] = lambda: self.del_all_garbage()

    def del_user(self):
        self.station.to_program("删除用户")

    def del_users(self):
        self.station.to_program("删除多个用户")

    def del_garbage(self):
        self.station.to_program("删除垃圾袋")

    def del_garbage_more(self):
        self.station.to_program("删除多个垃圾袋")

    def del_all_garbage(self):
        self.station.to_program("删除所有垃圾袋")


class SearchMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "搜索")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(6)]
        self.btn_name = ["用户", "高级搜索-用户", "垃圾袋", "高级搜索-垃圾袋", "高级搜索", "数据分析"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.user_command()
        self.btn[1]['command'] = lambda: self.user_advanced_command()
        self.btn[2]['command'] = lambda: self.garbage_command()
        self.btn[3]['command'] = lambda: self.garbage_advanced_command()
        self.btn[4]['command'] = lambda: self.advanced_command()
        self.btn[5]['command'] = lambda: self.statistics_command()

    def user_command(self):
        self.station.to_program("搜索用户")

    def user_advanced_command(self):
        self.station.to_program("高级搜索-用户")

    def garbage_command(self):
        self.station.to_program("搜索垃圾袋")

    def garbage_advanced_command(self):
        self.station.to_program("高级搜索-垃圾袋")

    def advanced_command(self):
        self.station.to_program("高级搜索")

    def statistics_command(self):
        self.station.to_menu("数据分析")


class UpdateMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "更新")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(4)]
        self.btn_name = ["用户-积分", "用户-累计分类信用", "垃圾袋-垃圾类型", "垃圾袋-检测结果"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)
        self.btn[0]['command'] = lambda: self.update_score_command()
        self.btn[1]['command'] = lambda: self.update_reputation_command()
        self.btn[2]['command'] = lambda: self.update_garbage_type_command()
        self.btn[3]['command'] = lambda: self.update_garbage_result_command()

    def update_reputation_command(self):
        self.station.to_program("更新用户-垃圾分类信用")

    def update_score_command(self):
        self.station.to_program("更新用户-积分")

    def update_garbage_type_command(self):
        self.station.to_program("更新垃圾袋-垃圾类型")

    def update_garbage_result_command(self):
        self.station.to_program("更新垃圾袋-检测结果")


class StatisticsMenu(AdminMenu):
    def __init__(self, station, win, color):
        super().__init__(station, win, color, "数据分析")
        self.btn: List[tk.Button] = [tk.Button(self.frame) for _ in range(5)]
        self.btn_name = ["时间分析", "积分分析", "信用分析", "失信用户", "通过率"]

    def conf_gui(self, color: str, n: int = 1):
        super().conf_gui(color, n)


all_menu = [MainMenu, CreateMenu, DeleteMenu, SearchMenu, UpdateMenu, StatisticsMenu]
