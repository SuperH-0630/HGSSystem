import conf
import tkinter as tk
import tkinter.font as font
from tool.type_ import *


class RankingStationException(Exception):
    ...


class RankingStatus:
    status_normal = 1
    status_get_garbage_type = 2
    status_get_garbage_check = 3

    def __init__(self, win):
        self._win: RankingStation = win
        self.rank = [[]]
        self.rank_index = 0

    def get_show_rank(self):
        rank_list = self.ranking()
        self.rank = [[]]
        for i, r in enumerate(rank_list):
            if len(self.rank[-1]) == 5:
                self.rank.append([])
            color = None
            if i == 0:
                color = "#eaff56"
            elif i == 1:
                color = "#ffa631"
            elif i == 2:
                color = "#ff7500"
            self.rank[-1].append((i + 1, r[1], r[0], r[2], r[3], color))

        self.rank_index = 0
        self.show_rank(0)

    def show_rank(self, n: int):
        self.update_user_time()
        self.rank_index += n

        if self.rank_index < 0 or self.rank_index >= len(self.rank):
            return

        self._win.show_rank(self.rank_index + 1, len(self.rank),
                            lambda: self.show_rank(-1),
                            lambda: self.show_rank(+1),
                            self.rank[self.rank_index])


class RankingStation:
    def __init__(self, refresh_delay: int = conf.tk_refresh_delay):
        self.refresh_delay = refresh_delay
        self._status = RankingStatus(self)

        self._window = tk.Tk()
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))
        self._win_width = int(self._sys_width * (1 / 3))
        self._full_screen = False
        self.__conf_windows()

        self.__conf_font_size()
        self.__creat_tk()
        self.__conf_tk()

    def __creat_tk(self):
        self._rank_frame = tk.Frame(self._window)
        self._rank_title = tk.Label(self._rank_frame)
        self._rank_title_var = tk.StringVar()
        self._rank_count = 7
        self._rank_label = [tk.Label(self._rank_frame) for _ in range(self._rank_count)]
        self._rank_y_height: List[Tuple[float, float]] = []  # rank 标签的y坐标信息
        self._rank_var = [tk.StringVar() for _ in range(self._rank_count)]
        self._rank_btn = [tk.Button(self._rank_frame) for _ in range(3)]  # prev, auto, next

    def __conf_font_size(self, n: Union[int, float] = 1):
        self._rank_font_title_size = int(24 * n)
        self._rank_font_size = int(16 * n)
        self._rank_font_btn_size = int(20 * n)

    def __conf_tk(self):
        self.__conf_rank()

    def __conf_windows(self):
        self._window.title('HGSSystem: Ranking')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = "#F0FFF0"  # 蜜瓜绿
        self._window.resizable(False, False)

    def __conf_rank(self):
        title_font = self.__make_font(size=self._rank_font_title_size, weight="bold")
        info_font = self.__make_font(size=self._rank_font_size)
        btn_font = self.__make_font(size=self._rank_font_btn_size)

        height = self._win_height * 0.95
        width = height * (3 / 4)

        # 宽度过大
        if width >= self._win_width:
            width = self._win_width * 0.95
            height = width * (4 / 3) / self._win_width

        relwidth = width / self._win_width
        relheight = height / self._win_height
        relx = (1 - relwidth) / 2
        rely = (1 - relheight) / 2

        self._rank_frame['relief'] = "ridge"
        self._rank_frame['bd'] = 5
        self._rank_frame['bg'] = "#F5F5DC"
        self._rank_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

        self._rank_title['font'] = title_font
        self._rank_title['bg'] = "#F5F5DC"
        self._rank_title['textvariable'] = self._rank_title_var
        self._rank_title.place(relx=0.02, rely=0.00, relwidth=0.96, relheight=0.1)
        self._rank_title_var.set("Ranking.loading...")

        """
        标签所拥有的总高度为0.82
        标签数为c
        间隔数为c-1
        标签高度为x
        间隔高度为y
        规定 5y = x
        所以: cx + (c - 1)y = 0.82
        得到: 5cx + (c - 1)y = (5c + c - 1)y = 0.82
        因此: x = 0.82 / (5c + c - 1)
        """

        height_s = (0.82 / (self._rank_count * 6 - 1))  # 标签的高度
        height_l = height_s * 5  # 间隔的高度

        height = 0.10  # 从 0.10 到 0.82
        for i in range(self._rank_count):
            self._rank_label[i]['font'] = info_font
            self._rank_label[i]['bg'] = "#F5FFFA"
            self._rank_label[i]['textvariable'] = self._rank_var[i]
            self._rank_label[i]['relief'] = "ridge"
            self._rank_label[i]['bd'] = 2
            self._rank_var[i].set("")
            self._rank_y_height.append((height, height_l))
            height += height_l + height_s

        for btn, text, x in zip(self._rank_btn, ("prev", "close", "next"), (0.050, 0.375, 0.700)):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = "#00CED1"
            btn['state'] = "disable"
            btn.place(relx=x, rely=0.93, relwidth=0.25, relheight=0.06)
        self.show_rank()

    # def set_rank_info(self, page, page_c, prev_func: Callable, next_func: Callable,
    #                   rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
    #     if len(rank_info) > 5:
    #         rank_info = rank_info[:5]
    #
    #     for lb in self._rank_label[1:]:  # 隐藏全部标签
    #         lb.place_forget()
    #
    #     height = 0.12
    #     for i, info in enumerate(rank_info):
    #         no, name, uid, score, eval_, color = info
    #         self._rank_var[i + 1].set(f"NO.{no}  {name}\nUID: {uid[0:conf.ranking_tk_show_uid_len]}\n"
    #                                   f"Score: {score} Reputation: {eval_}")
    #         if color is None:
    #             self._rank_label[i + 1]['bg'] = "#F5FFFA"
    #         else:
    #             self._rank_label[i + 1]['bg'] = color
    #
    #         self._rank_label[i + 1].place(relx=0.04, rely=height, relwidth=0.92, relheight=0.13)
    #         height += 0.15
    #
    #     self._rank_btn[0]['command'] = prev_func
    #     self._rank_btn[0]['state'] = 'normal'
    #     self._rank_btn[1]['command'] = lambda: self.hide_msg_rank(True)
    #     self._rank_btn[2]['command'] = next_func
    #     self._rank_btn[2]['state'] = 'normal'
    #
    #     if page == 1:
    #         self._rank_btn[0]['state'] = 'disable'
    #     if page == page_c:
    #         self._rank_btn[2]['state'] = 'disable'

    def show_rank(self, *args):
        for i in range(self._rank_count):
            rely = self._rank_y_height[i][0]
            relheight = self._rank_y_height[i][1]
            self._rank_label[i].place(relx=0.04, rely=rely, relwidth=0.92, relheight=relheight)

    @staticmethod
    def __make_font(family: str = 'noto', **kwargs):
        return font.Font(family=conf.font_d[family], **kwargs)

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()


if __name__ == '__main__':
    station = RankingStation()
    station.mainloop()
