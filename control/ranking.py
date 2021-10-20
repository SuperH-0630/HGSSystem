import tkinter as tk
import tkinter.font as font
from PIL import Image, ImageTk

import conf

from tool.type_ import *

from sql.db import DB


class RankingStationException(Exception):
    ...


class RankingError(RankingStationException):
    ...


class RankingPageError(RankingStationException):
    ...


class RankingStatus:
    status_normal = 1
    status_get_garbage_type = 2
    status_get_garbage_check = 3

    def __init__(self, win, db: DB):
        self._win: RankingStation = win
        self._db = db
        self.rank = [[]]

        self.rank_index = 0
        self.rank_count = 1

        self.offset = 0
        self.limit_n = 2

    def get_rank(self, offset: int = 0) -> Tuple[bool, list]:
        limit = self.rank_count * self.limit_n
        offset = self.offset + limit * offset  # offset为0表示不移动, 1表示向前, -1表示向后
        cur = self._db.search((f"SELECT uid, name, score, reputation "
                               f"FROM user "
                               f"WHERE manager = 0 "
                               f"ORDER BY reputation DESC, score DESC "
                               f"LIMIT {limit} OFFSET {offset};"))
        if cur is None or cur.rowcount == 0:
            return False, []
        self.offset = offset

        rank_list = list(cur.fetchall())

        rank = [[]]
        for i, r in enumerate(rank_list):
            if len(rank[-1]) == self.rank_count:
                rank.append([])
            color = None
            if self.offset + i == 0:
                color = "#eaff56"
            elif self.offset + i == 1:
                color = "#ffa631"
            elif self.offset + i == 2:
                color = "#ff7500"
            rank[-1].append((self.offset + i + 1, r[1], r[0], r[2], r[3], color))

        return True, rank

    def rank_page_to_next(self):
        if self.rank_index == len(self.rank) - 1:
            self._win.set_next_btn(True)  # 当 rank_index为最后一项时, 该函数不应该被调用(除非数据库被外部改动)
            return

        self.rank_index += 1
        if self.rank_index == len(self.rank) - 1:  # 最后一项
            if len(self.rank[self.rank_index]) == self.rank_count:
                res, rank = self.get_rank(1)  # 向前移动一个offset
                if res:
                    self.rank = self.rank[self.rank_index], *rank  # 调整rank的内容
                    self.rank_index = 0
                else:
                    self._win.set_next_btn(True)
            else:  # 如果最后一个表格没有填满, 直接判定无next
                self._win.set_next_btn(True)
        self._win.show_rank(self.rank[self.rank_index])
        self._win.set_prev_btn(False)

    def rank_page_to_prev(self):
        if self.rank_index == 0:  # 当 rank_index为最后一项时, 该函数不应该被调用(除非数据库被外部改动)
            self._win.set_prev_btn(True)
            return

        self.rank_index -= 1
        if self.rank_index == 0:  # 回到第一项
            res, rank = self.get_rank(-1)  # 向后移动一个offset
            if res:
                self.rank = *rank, self.rank[self.rank_index]  # 调整rank的内容
                self.rank_index = 0
            else:
                self._win.set_prev_btn(True)
        self._win.show_rank(self.rank[self.rank_index])
        self._win.set_next_btn(False)

    def show_rank(self):
        self.rank_index = 0
        self.offset = 0
        self.rank_count = self._win.get_rank_count()
        res, self.rank = self.get_rank(0)

        self._win.show_rank(self.rank[0])

        self._win.set_prev_btn(True)
        if len(self.rank) == 1:
            self._win.set_next_btn(True)
        else:
            self._win.set_next_btn(False)


class RankingStation:
    def __init__(self, db: DB, refresh_delay: int = conf.tk_refresh_delay):
        self.refresh_delay = refresh_delay
        self._status = RankingStatus(self, db)

        self._window = tk.Tk()
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))
        self._win_width = int(self._sys_width * (1 / 3))
        self._full_screen = False
        self.__conf_windows()

        self._next_btn: bool = True  # 表示开关是否启用
        self._prev_btn: bool = True
        self._auto: bool = False
        self._auto_to_next: bool = True  # auto的移动方向
        self._auto_time: int = 5000  # 5s

        self.__conf_font_size()
        self.__creat_tk()
        self.__conf_tk()
        self._status.show_rank()

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
        self.__conf_windows_bg()
        self.__conf_rank()

    def __conf_windows(self):
        self._window.title('HGSSystem: Ranking')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = "#F0FFF0"  # 蜜瓜绿
        self._window.resizable(False, False)
        self.bg_img = None
        self.bg_lb = tk.Label(self._window)
        self.bg_lb['bg'] = "#F0FFF0"  # 蜜瓜绿
        self.bg_lb.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._window.bind("<F11>", lambda _: self.__switch_full_screen())

    def __conf_windows_bg(self):
        img = Image.open(conf.pic_d['rank_bg']).resize((self._win_width, self._win_height))
        self.bg_img = ImageTk.PhotoImage(img)
        self.bg_lb['image'] = self.bg_img
        self.bg_lb.place(relx=0, rely=0, relwidth=1, relheight=1)

    def __switch_full_screen(self):
        self._full_screen = not self._full_screen
        self._window.attributes("-fullscreen", self._full_screen)

        width = self._sys_width * (1 / 3)
        height = self._sys_height * (2 / 3)
        self._win_width = self._window.winfo_width()
        self._win_height = self._window.winfo_height()

        n = min((self._win_height / height), (self._win_width / width))  # 因为横和纵不是平均放大, 因此取倍数小的
        self.__conf_font_size(n)
        self.__conf_tk()
        self._status.show_rank()

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

        for btn, text, x in zip(self._rank_btn,
                                ("prev", "manual" if self._auto else "auto", "next"), (0.050, 0.375, 0.700)):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = "#00CED1"
            btn.place(relx=x, rely=0.93, relwidth=0.25, relheight=0.06)

        self._rank_btn[0]['command'] = lambda: self._status.rank_page_to_prev()
        self._rank_btn[1]['command'] = lambda: self.rank_auto(True)
        self._rank_btn[2]['command'] = lambda: self._status.rank_page_to_next()

    def set_rank_info(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        if len(rank_info) > self._rank_count:
            rank_info = rank_info[:self._rank_count]

        for lb in self._rank_label:  # 隐藏全部标签
            lb.place_forget()

        for i, info in enumerate(rank_info):
            no, name, uid, score, eval_, color = info
            self._rank_var[i].set(f"NO.{no}  {name}\nUID: {uid[0:conf.ranking_tk_show_uid_len]}\n"
                                  f"Score: {score} Reputation: {eval_}")
            if color is None:
                self._rank_label[i]['bg'] = "#F5FFFA"
            else:
                self._rank_label[i]['bg'] = color

            rely = self._rank_y_height[i][0]
            relheight = self._rank_y_height[i][1]
            self._rank_label[i].place(relx=0.04, rely=rely, relwidth=0.92, relheight=relheight)

    def show_rank(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        self.set_rank_info(rank_info)
        self._rank_title_var.set("Ranking")

    def rank_auto(self, auto):
        if auto:
            self._rank_btn[1]['command'] = lambda: self.rank_auto(False)
            self._rank_btn[1]['text'] = 'manual'
            self._auto = True
            self._window.after(self._auto_time, self.update_rank_auto)  # 注册自动函数
            self.disable_btn()
        else:
            self._rank_btn[1]['command'] = lambda: self.rank_auto(True)
            self._rank_btn[1]['text'] = 'auto'
            self._auto = False
            self.able_btn()

    def update_rank_auto(self):
        if not self._auto:
            return

        if (self._auto_to_next and self._next_btn or
                not self._auto_to_next and not self._prev_btn and self._next_btn):
            self._status.rank_page_to_next()
            self._auto_to_next = True
        elif (not self._auto_to_next and self._prev_btn or
              self._auto_to_next and not self._next_btn and self._prev_btn):
            self._status.rank_page_to_prev()
            self._auto_to_next = False
        else:
            return  # 无法动弹

        self._window.after(self._auto_time, self.update_rank_auto)

    @staticmethod
    def __make_font(family: str = 'noto', **kwargs):
        return font.Font(family=conf.font_d[family], **kwargs)

    def set_next_btn(self, disable: False):
        if disable or self._auto:  # auto 模式令btn失效
            self._rank_btn[2]['state'] = 'disable'
        else:
            self._rank_btn[2]['state'] = 'normal'
        self._next_btn = not disable

    def set_prev_btn(self, disable: False):
        if disable or self._auto:
            self._rank_btn[0]['state'] = 'disable'
        else:
            self._rank_btn[0]['state'] = 'normal'
        self._prev_btn = not disable

    def disable_btn(self):
        self._rank_btn[0]['state'] = 'disable'
        self._rank_btn[2]['state'] = 'disable'

    def able_btn(self):
        if self._prev_btn:
            self._rank_btn[0]['state'] = 'normal'
        if self._next_btn:
            self._rank_btn[2]['state'] = 'normal'

    def get_rank_count(self):
        return self._rank_count

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()


if __name__ == '__main__':
    mysql_db = DB()
    station = RankingStation(mysql_db)
    station.mainloop()
