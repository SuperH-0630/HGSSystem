import abc
import tkinter as tk
from PIL import Image, ImageTk

from conf import Config
from tool.type_ import *
from tool.tk import make_font
from sql.db import DB


class RankingStationBase(metaclass=abc.ABCMeta):
    """
    RankingStation基类
    封装排行榜相关操作
    """

    def __init__(self, db: DB):
        self._db = db
        self.rank = [[]]

        self.rank_index = 0
        self.rank_count = 1

        self.offset = 0
        self.limit_n = 2  # 一次性获取的数据 (页数, 行数=limit_n * rank_count)

        self.auto: bool = False
        self.auto_to_next: bool = True  # auto的移动方向
        self.auto_time: int = 5000  # 5s

    def get_rank(self, offset: int = 0) -> Tuple[bool, list]:
        """
        获取数据
        :param offset: 位移 (相对于当前位置移动的页数)
        :return: 成功, 排行榜数据
        """
        limit = self.rank_count * self.limit_n
        offset = self.offset + limit * offset  # offset为0表示不移动, 1表示向前, -1表示向后
        if offset < 0:
            return False, []

        cur = self._db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                              table='user',
                              where='IsManager=0',
                              order_by=[('Reputation', "DESC"), ('Score', "DESC"), ('UserID', "DESC")],
                              limit=limit,
                              offset=offset)
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
        """
        显示排行榜下一页数据
        :return:
        """
        if self.rank_index == len(self.rank) - 1:
            self.set_next_btn(True)  # 当 rank_index为最后一项时, 该函数不应该被调用(除非数据库被外部改动)
            return

        self.rank_index += 1
        if self.rank_index == len(self.rank) - 1:  # 最后一项
            if len(self.rank[self.rank_index]) == self.rank_count:
                res, rank = self.get_rank(1)  # 向前移动一个offset
                if res:
                    self.rank = self.rank[self.rank_index], *rank  # 调整rank的内容
                    self.rank_index = 0
                else:
                    self.set_next_btn(True)
            else:  # 如果最后一个表格没有填满, 直接判定无next
                self.set_next_btn(True)
        self.show_rank(self.rank[self.rank_index])
        self.set_prev_btn(False)

        if self.auto:
            self.set_run_after_now(self.auto_time, self.update_rank_auto)

    def rank_page_to_prev(self):
        """
        显示排行榜上一页数据
        :return:
        """
        if self.rank_index == 0:  # 当 rank_index为最后一项时, 该函数不应该被调用(除非数据库被外部改动)
            self.set_prev_btn(True)
            return

        self.rank_index -= 1
        if self.rank_index == 0:  # 回到第一项
            res, rank = self.get_rank(-1)  # 向后移动一个offset
            if res:
                self.rank = *rank, self.rank[self.rank_index]  # 调整rank的内容
                self.rank_index = 0
            else:
                self.set_prev_btn(True)
        self.show_rank(self.rank[self.rank_index])
        self.set_next_btn(False)

        if self.auto:
            self.set_run_after_now(self.auto_time, self.update_rank_auto)

    def show_rank_first(self):
        """
        第一次显示排行榜数据
        :return:
        """
        self.rank_index = 0
        self.offset = 0
        self.rank_count = self.rank_count
        res, self.rank = self.get_rank(0)

        if not res:
            self.set_next_btn(False)
            self.set_prev_btn(False)
            self.show_rank([])
            return

        self.show_rank(self.rank[0])

        self.set_prev_btn(True)
        if len(self.rank) == 1:
            self.set_next_btn(True)
        else:
            self.set_next_btn(False)

    def rank_auto(self, auto):
        """
        启用或关闭自动显示
        :param auto: True-启用自动显示, False-关闭
        :return:
        """
        if auto:
            self.auto = True
            self.disable_btn()
            self.set_run_after_now(self.auto_time, self.update_rank_auto)  # 注册自动函数
        else:
            self.auto = False
            self.able_btn()

    def update_rank_auto(self):
        """
        自动显示
        :return:
        """
        if not self.auto:
            return

        if (self.auto_to_next and self.is_able_next() or
                not self.auto_to_next and not self.is_able_prev() and self.is_able_next()):
            self.rank_page_to_next()
            self.auto_to_next = True
        elif (not self.auto_to_next and self.is_able_prev() or
              self.auto_to_next and not self.is_able_next() and self.is_able_prev()):
            self.rank_page_to_prev()
            self.auto_to_next = False
        else:
            return  # 无法动弹

    @abc.abstractmethod
    def show_rank(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        ...

    @abc.abstractmethod
    def set_next_btn(self, disable: False):
        ...

    @abc.abstractmethod
    def set_prev_btn(self, disable: False):
        ...

    @abc.abstractmethod
    def disable_btn(self):
        ...

    @abc.abstractmethod
    def able_btn(self):
        ...

    @abc.abstractmethod
    def is_able_prev(self):
        ...

    @abc.abstractmethod
    def is_able_next(self):
        ...

    @abc.abstractmethod
    def set_run_after_now(self, ms, func, *args):
        ...

    @abc.abstractmethod
    def mainloop(self):
        ...


class RankingStation(RankingStationBase):
    """
        RankingStation 排行榜系统
        使用tkinter作为GUI
        派生自 GarbageStation
        """

    def __init__(self, db: DB):
        self.init_after_run_list: List[Tuple[int, Callable, Tuple]] = []
        super(RankingStation, self).__init__(db)

        self.window = tk.Tk()
        self._sys_height = self.window.winfo_screenheight()
        self._sys_width = self.window.winfo_screenwidth()

        self.height = int(self._sys_height * (2 / 3))
        self.width = int(self._sys_width * (1 / 3))
        self._full_screen = False
        self.__conf_windows()

        self.next_btn: bool = True  # 表示按键是否启用
        self.prev_btn: bool = True

        self.__conf_font_size()
        self.__create_tk()
        self.__conf_tk()

        self.show_rank_first()

    def __create_tk(self):
        self.rank_frame = tk.Frame(self.window)
        self.rank_title = tk.Label(self.rank_frame)
        self.rank_title_var = tk.StringVar()
        self.rank_count = 7  # 一页显示的行数
        self.rank_label = [tk.Label(self.rank_frame) for _ in range(self.rank_count)]
        self.rank_y_height: List[Tuple[float, float]] = []  # rank_web 标签的y坐标信息
        self.rank_var = [tk.StringVar() for _ in range(self.rank_count)]
        self.rank_btn = [tk.Button(self.rank_frame) for _ in range(3)]  # prev, auto, next

    def __conf_font_size(self, n: Union[int, float] = 1):
        self._rank_font_title_size = int(24 * n)
        self._rank_font_size = int(16 * n)
        self._rank_font_btn_size = int(16 * n)

    def __conf_tk(self):
        self.__conf_windows_bg()
        self.__conf_rank()

    def __conf_windows(self):
        self.window.title('HGSSystem: Ranking')
        self.window.geometry(f'{self.width}x{self.height}')
        self.window['bg'] = Config.tk_win_bg
        self.window.resizable(False, False)
        self.bg_img = None
        self.bg_lb = tk.Label(self.window)
        self.bg_lb['bg'] = Config.tk_win_bg
        self.bg_lb.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.window.bind("<F11>", lambda _: self.__switch_full_screen())

    def __conf_windows_bg(self):
        img = Image.open(Config.picture_d['rank_bg']).resize((self.width, self.height), Image.ANTIALIAS)
        self.bg_img = ImageTk.PhotoImage(img)
        self.bg_lb['image'] = self.bg_img
        self.bg_lb.place(relx=0, rely=0, relwidth=1, relheight=1)

    def __switch_full_screen(self):
        self._full_screen = not self._full_screen
        self.window.attributes("-fullscreen", self._full_screen)

        width = self._sys_width * (1 / 3)
        height = self._sys_height * (2 / 3)
        self.width = self.window.winfo_width()
        self.height = self.window.winfo_height()

        n = min((self.height / height), (self.width / width))  # 因为横和纵不是平均放大, 因此取倍数小的
        self.__conf_font_size(n)
        self.__conf_tk()
        self.show_rank_first()

    def __conf_rank(self):
        title_font = make_font(size=self._rank_font_title_size, weight="bold")
        info_font = make_font(size=self._rank_font_size)
        btn_font = make_font(size=self._rank_font_btn_size)

        height = self.height * 0.95
        width = height * (3 / 4)

        # 宽度过大
        if width >= self.width:
            width = self.width * 0.95
            height = width * (4 / 3) / self.width

        relwidth = width / self.width
        relheight = height / self.height
        relx = (1 - relwidth) / 2
        rely = (1 - relheight) / 2

        self.rank_frame['relief'] = "ridge"
        self.rank_frame['bd'] = 5
        self.rank_frame['bg'] = Config.tk_second_win_bg
        self.rank_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

        self.rank_title['font'] = title_font
        self.rank_title['bg'] = Config.tk_second_win_bg
        self.rank_title['textvariable'] = self.rank_title_var
        self.rank_title.place(relx=0.02, rely=0.00, relwidth=0.96, relheight=0.1)
        self.rank_title_var.set("排行榜加载中...")

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

        height_s = (0.82 / (self.rank_count * 6 - 1))  # 标签的高度
        height_l = height_s * 5  # 间隔的高度

        height = 0.10  # 从 0.10 到 0.82
        for i in range(self.rank_count):
            self.rank_label[i]['font'] = info_font
            self.rank_label[i]['bg'] = "#F5FFFA"
            self.rank_label[i]['textvariable'] = self.rank_var[i]
            self.rank_label[i]['relief'] = "ridge"
            self.rank_label[i]['bd'] = 2
            self.rank_var[i].set("")
            self.rank_y_height.append((height, height_l))
            height += height_l + height_s

        for btn, text, x in zip(self.rank_btn,
                                ("上一页", "手动" if self.auto else "自动", "下一页"), (0.050, 0.375, 0.700)):
            btn['font'] = btn_font
            btn['text'] = text
            btn['bg'] = Config.tk_btn_bg
            btn.place(relx=x, rely=0.93, relwidth=0.25, relheight=0.06)

        self.rank_btn[0]['command'] = lambda: self.rank_page_to_prev()
        self.rank_btn[1]['command'] = lambda: self.rank_auto(True)
        self.rank_btn[2]['command'] = lambda: self.rank_page_to_next()

    def set_run_after_now(self, ms, func, *args):
        self.window.after(ms, func, *args)

    def __set_rank_info(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        if len(rank_info) > self.rank_count:
            rank_info = rank_info[:self.rank_count]

        for lb in self.rank_label:  # 隐藏全部标签
            lb.place_forget()

        for i, info in enumerate(rank_info):
            no, name, uid, score, eval_, color = info
            self.rank_var[i].set(f"NO.{no}  {name}\n\n"  # 中间空一行 否则中文字体显得很窄
                                 f"ID: {uid[0:Config.ranking_tk_show_uid_len]}  "
                                 f"信用: {eval_} 积分: {score}")
            if color is None:
                self.rank_label[i]['bg'] = "#F5FFFA"
            else:
                self.rank_label[i]['bg'] = color

            rely = self.rank_y_height[i][0]
            relheight = self.rank_y_height[i][1]
            self.rank_label[i].place(relx=0.04, rely=rely, relwidth=0.92, relheight=relheight)

    def show_rank(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        if len(rank_info) == 0:
            self.rank_title_var.set("排行榜无数据")
        else:
            self.__set_rank_info(rank_info)
            self.rank_title_var.set("排行榜")

    def rank_auto(self, auto):
        super(RankingStation, self).rank_auto(auto)
        if auto:
            self.rank_btn[1]['command'] = lambda: self.rank_auto(False)
            self.rank_btn[1]['text'] = '手动'
        else:
            self.rank_btn[1]['command'] = lambda: self.rank_auto(True)
            self.rank_btn[1]['text'] = '自动'

    def set_next_btn(self, disable: False):
        if disable or self.auto:  # auto 模式令btn失效
            self.rank_btn[2]['state'] = 'disable'
        else:
            self.rank_btn[2]['state'] = 'normal'
        self.next_btn = not disable

    def set_prev_btn(self, disable: False):
        if disable or self.auto:
            self.rank_btn[0]['state'] = 'disable'
        else:
            self.rank_btn[0]['state'] = 'normal'
        self.prev_btn = not disable

    def disable_btn(self):
        self.rank_btn[0]['state'] = 'disable'
        self.rank_btn[2]['state'] = 'disable'

    def able_btn(self):
        if self.prev_btn:
            self.rank_btn[0]['state'] = 'normal'
        if self.next_btn:
            self.rank_btn[2]['state'] = 'normal'

    def is_able_prev(self):
        return self.prev_btn

    def is_able_next(self):
        return self.next_btn

    def mainloop(self):
        self.window.mainloop()
