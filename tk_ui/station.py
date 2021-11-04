import os.path
import time
import tempfile
import cv2.cv2 as cv2
import random
import traceback
import abc
import tkinter as tk
from tkinter import ttk
import datetime
from PIL import Image, ImageTk

from conf import Config
from tool.type_ import *
from tool.tk import set_tk_disable_from_list, make_font
from tool.thread_ import getThreadIdent

from core.user import User
from core.garbage import GarbageBag, GarbageType

from sql.db import DB
from sql.user import update_user, find_user_by_id
from sql.garbage import update_garbage

from equipment.scan import HGSCapture, HGSQRCoder
from equipment.aliyun import Aliyun, AliyunClientException, AliyunServerException

from .event import TkEventMain


class GarbageStationBase(TkEventMain, metaclass=abc.ABCMeta):
    """
    GarbageStation基类
    封装GarbageStation的相关操作
    主要是柯里化 QR, sql相关函数
    """

    # 操作状态
    status_normal = 1
    status_get_garbage_type = 2
    status_get_garbage_check = 3

    # 扫码状态
    scan_switch_user = 1
    scan_throw_garbage = 2
    scan_check_garbage = 3
    scan_no_to_done = 4

    def __init__(self,
                 db: DB,
                 cap: HGSCapture,
                 qr: HGSQRCoder,
                 aliyun: Aliyun,
                 loc: location_t = Config.base_location):
        self._db: DB = db
        self._cap: HGSCapture = cap
        self._qr: HGSQRCoder = qr
        self._aliyun: Aliyun = aliyun
        self._loc: location_t = loc

        self._user: Optional[User] = None  # 操作者
        self._user_last_time: time_t = 0

        self._garbage: Optional[GarbageBag] = None

        self._flat = GarbageStationBase.status_normal
        self._have_easter_eggs = False

        self.rank = None
        self.rank_index = 0

        self.search_time = 0  # 上次执行搜索任务的时间
        super(GarbageStationBase, self).__init__()

    def get_db(self):
        return self._db

    def update_user_time(self):
        if self.check_user():
            self._user_last_time = time.time()

    def get_user(self):
        return self._user

    def is_manager(self):
        if not self.check_user():
            return False
        return self._user.is_manager()

    def check_user(self):
        if self._user is None:
            return False
        if not self._user.is_manager() and time.time() - self._user_last_time > 20:
            self._user = None
            return False
        return True

    def __check_normal_user(self):
        if self.check_user() and not self._user.is_manager():
            return True
        return False

    def __check_manager_user(self):
        if self.check_user() and self._user.is_manager():
            return True
        return False

    def get_user_info(self):
        assert self.check_user()
        return self._user.get_info()

    def get_uid_no_update(self):
        if not self.check_user():
            return ""
        return self._user.get_uid()

    def get_user_info_no_update(self) -> Dict[str, str]:
        if not self.check_user():
            return {}
        return self._user.get_info()

    def get_cap_img(self):
        return self._cap.get_frame()

    def switch_user(self, user: User) -> bool:
        """
        切换用户: 退出/登录
        :param user: 新用户
        :return: 登录-True, 退出-False
        """
        if self._user is not None and self._user.get_uid() == user.get_uid() and self.check_user():  # 正在登陆期
            self._user = None  # 退出登录
            self._user_last_time = 0
            self.show_msg("退出登录", "退出登录成功", show_time=3.0)
            return False
        self._user = user
        self._user_last_time = time.time()
        self.show_msg("登录", "登录成功", show_time=3.0)
        return True  # 登录

    def throw_garbage_core(self, garbage: GarbageBag, garbage_type: enum) -> int:
        if not self.__check_normal_user():
            return -1
        if not self._user.throw_rubbish(garbage, garbage_type, self._loc):
            return -2
        if not update_garbage(garbage, self._db):
            return -3
        if not update_user(self._user, self._db):
            return -3
        return 0

    def check_garbage_core(self, garbage: GarbageBag, check_result: bool) -> int:
        if not self.__check_manager_user():
            return -1
        user = find_user_by_id(garbage.get_user(), self._db)
        if user is None:
            return -2
        if not self._user.check_rubbish(garbage, check_result, user):
            return -3
        if not update_garbage(garbage, self._db):
            return -4
        if not update_user(self._user, self._db):
            return -4
        if not update_user(user, self._db):
            return -4
        return 0

    def ranking(self, limit: int = 0, order_by: str = 'DESC') -> list[Tuple[uid_t, uname_t, score_t, score_t]]:
        """
        获取排行榜的功能
        :return:
        """

        if order_by != 'ASC' and order_by != 'DESC':
            order_by = 'DESC'

        cur = self._db.search(columns=['UserID', 'Name', 'Score', 'Reputation'],
                              table='user',
                              where='IsManager=0',
                              order_by=[('Reputation', order_by), ('Score', order_by), ('UserID', order_by)],
                              limit=limit)
        if cur is None:
            return []
        return list(cur.fetchall())

    def to_get_garbage_type(self, garbage: GarbageBag):
        self._flat = GarbageStationBase.status_get_garbage_type
        self.set_garbage(garbage)

    def to_get_garbage_check(self, garbage: GarbageBag):
        self._flat = GarbageStationBase.status_get_garbage_check
        self.set_garbage(garbage)

    def set_garbage(self, garbage: GarbageBag):
        self._garbage = garbage

    def get_garbage(self) -> Optional[GarbageBag]:
        if not self.check_user():
            self._garbage = None
        return self._garbage

    def throw_garbage(self, garbage_type: enum):
        self.update_user_time()
        if self._flat != GarbageStationBase.status_get_garbage_type or self._garbage is None:
            self.show_warning("操作失败", "请先登录, 扫描垃圾袋")
            return

        event = tk_event.ThrowGarbageEvent(self).start(self._garbage, garbage_type)
        self.push_event(event)
        self._flat = GarbageStationBase.status_normal
        self._garbage = None

    def check_garbage(self, check: bool):
        self.update_user_time()
        if self._flat != GarbageStationBase.status_get_garbage_check or self._garbage is None:
            self.show_warning("操作失败", "请先登录, 扫描垃圾袋")
            return

        event = tk_event.CheckGarbageEvent(self).start(self._garbage, check)
        self.push_event(event)
        self._flat = GarbageStationBase.status_normal
        self._garbage = None

    def show_garbage_info(self):
        self.update_user_time()
        if self._flat != GarbageStationBase.status_get_garbage_check or self._garbage is None:
            self.show_warning("操作失败", "请先登录, 扫描垃圾袋")
            return

        if not self._garbage.is_use():
            self.show_warning("操作失败", "垃圾袋还未被使用")
            return

        info = self._garbage.get_info()
        garbage_type = GarbageType.GarbageTypeStrList_ch[int(info['type'])]
        if self._garbage.is_check()[0]:
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(info['use_time'])))
            check = f'Checker is {info["checker"][0:Config.show_uid_len]}\n'
            if info["check"] == '1':
                check += f'检查结果为 投放正确\n'
            else:
                check += f'检查结果为 投放错误\n'
            self.show_msg("垃圾袋信息", (f"垃圾类型为 {garbage_type}\n"
                                    f"用户是 {info['user'][0:Config.show_uid_len]}\n"
                                    f"地址:\n  {info['loc']}\n"
                                    f"{check}"
                                    f"使用日期:\n  {time_str}"), show_time=5.0)  # 遮蔽Pass和Fail按键
        elif self._garbage.is_use():
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(info['use_time'])))
            self.show_msg("垃圾袋信息", (f"垃圾类型为 {garbage_type}\n"
                                    f"用户是 {info['user'][0:Config.show_uid_len]}\n"
                                    f"地址:\n  {info['loc']}\n"
                                    f"垃圾袋还未检查\n"
                                    f"使用日期:\n  {time_str}"), big=False, show_time=5.0)  # 不遮蔽Pass和Fail按键
        else:
            self.show_msg("垃圾袋信息", f"垃圾袋还未使用", show_time=5.0)  # 遮蔽Pass和Fail按键

    def show_user_info(self):
        self.update_user_time()
        if not self.check_user():
            self.show_warning("操作失败", "请先登录")
            return

        info = self.get_user_info()
        if info.get('manager', '0') == '1':
            self.show_msg("About User", (f"管理者用户\n"
                                         f"用户名: {info['name']}\n"
                                         f"用户ID:\n  {info['uid']}"), show_time=5.0)
        else:
            self.show_msg("About User", (f"普通用户\n"
                                         f"用户名: {info['name']}\n"
                                         f"用户ID:\n  {info['uid']}\n"
                                         f"评分: {info['score']}\n"
                                         f"垃圾分类信用: {info['reputation']}\n"
                                         f"垃圾量(7天): {info['rubbish']}"), show_time=5.0)

    def show_help_info(self):
        self.update_user_time()
        self.show_msg("帮助", f'''
所有用户: 离开前请确保账户退出(再次扫描用户二维码退出登录)
        
投放垃圾使用说明（普通用户）:
  1) 扫码用户二维码登录
  2) 扫码垃圾袋二维码
  3) 选择垃圾类型
  4) 投放垃圾到垃圾桶 (投放完成, 可以离开或继续投放)
  5) 等待结果反馈 (可能需要数日)
  
检测垃圾使用说明（管理用户）:
  1) 扫码用户二维码登录
  2) 扫码垃圾袋二维码
  3) 检查垃圾是否投放正确
  4) 操作完成 (投放完成, 可以离开或继续投放)
        '''.strip(), show_time=60.0)

    def show_about_info(self):
        self.update_user_time()
        self.show_msg("关于", Config.about_info, show_time=5.0)

    def show_exit(self):
        self.update_user_time()
        if self.is_manager():
            self.exit_win()
            return
        self.show_warning("退出", f'用户不具有退出权限')

    def easter_eggs(self):
        self.update_user_time()
        if (not self._have_easter_eggs) and random.randint(0, 10) != 1:  # 10% 概率触发
            return
        self._have_easter_eggs = True
        self.show_msg("Easter Agg", f'''
恭喜触发彩蛋
尝试一下新的编程语言: aFunlang.
来自: github
[斯人若彩虹, 遇上方知有]
[期待再次与你相遇]
                '''.strip(), show_time=15.0)

    def thread_show_rank(self, rank_list):
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
            elif r[0] == self.get_uid_no_update():
                color = "#b0a4e3"
            self.rank[-1].append((i + 1, r[1], r[0], r[2], r[3], color))
        if len(self.rank[0]) == 0:
            self.rank = None
            self.show_warning("排行榜错误", f'无法获取排行榜信息')
            return
        self.rank_index = 0
        self.get_rank(0)

    def get_rank(self, n: int):
        self.update_user_time()
        self.rank_index += n

        if self.rank_index < 0 or self.rank_index >= len(self.rank):
            self.show_warning("排行榜错误", f'无法获取排行榜信息')
            return

        self.show_rank(self.rank_index + 1, len(self.rank), self.rank[self.rank_index])

    def scan(self):
        """
        处理扫码事务
        二维码扫描的任务包括: 登录, 扔垃圾, 标记垃圾
        :return:
        """
        self._cap.get_image()
        qr_code = self._qr.get_qr_code()
        if qr_code is None:
            return GarbageStationBase.scan_no_to_done, None

        user_scan_event = tk_event.ScanUserEvent(self).start(qr_code)
        self.push_event(user_scan_event)

    def get_show_rank(self):
        event = tk_event.RankingEvent(self)
        self.push_event(event)

    def search_core(self, temp_dir: tempfile.TemporaryDirectory, file_path: str) -> Optional[Dict]:
        try:
            img_url = self._aliyun.oss_file(file_path, "jpg", True)
            res = self._aliyun.garbage_search(img_url)
        except (AliyunClientException, AliyunServerException):
            return None
        else:
            return res
        finally:
            temp_dir.cleanup()

    def get_search_result(self, res: dict) -> bool:
        self.search_time = time.time()
        data: Optional[dict] = res.get("Data")
        if data is None:
            self.show_warning("搜索垃圾", "搜索垃圾时发生错误")
            return False

        sensitive = data.get("Sensitive")
        if sensitive is None:
            self.show_warning("搜索垃圾", "搜索垃圾时发生错误")
            return False
        elif sensitive:
            self.show_warning("搜索垃圾", "图片不够清晰")  # 图片违规
            return False
        elements: List[Dict] = data.get("Elements")
        assert elements is not None

        res_str = f"搜索结果为 [共{len(elements)}项]:\n\n"
        for i, element in enumerate(elements):
            name_ = element.get("Rubbish")
            name_score = element.get("RubbishScore")
            if len(name_) == 0:
                name = "未知物品"
            else:
                name = f"{name_} [可信度: {name_score * 100}%]"
            if name_score < 0.001:
                name_score = 0.01
            category_ = element.get("Category")
            category_score = element.get("CategoryScore")
            if len(category_) == 0:
                category = "未知垃圾类型"
            else:
                category_ = {"可回收垃圾": "可回收垃圾",
                             "干垃圾": "其他垃圾",
                             "湿垃圾": "厨余垃圾",
                             "有害垃圾": "有害垃圾"}.get(category_, "未知垃圾类型")
                category_score = category_score / name_score
                if category_score > 1:
                    category_score = 1
                category = f"垃圾类型为{category_} [可信度: {category_score * 100}%]"
            res_str += f"  NO.{i + 1} {name}\n  {category}\n"
        self.show_msg("搜索垃圾", res_str, show_time=30, big=True)

    def search_pic(self, img: Image.Image) -> bool:
        sep = time.time() - self.search_time
        if sep < 3:
            self.show_warning("搜索垃圾", f"搜索太频繁了\n请稍后再尝试")
            return False
        elif sep <= Config.search_reset_time:
            self.show_warning("搜索垃圾", f"搜索太频繁了\n请{int(sep)}s后再尝试")
            return False

        temp_dir = tempfile.TemporaryDirectory()
        tid = getThreadIdent()
        file_path = os.path.join(temp_dir.name, f"search-{tid}.jpg")
        img.save(file_path, 'JPEG', quality=100)
        event = tk_event.SearchGarbageEvent(self).start(temp_dir, file_path)
        self.push_event(event)
        return True

    @abc.abstractmethod
    def show_msg(self, title, info, msg_type='info', big: bool = True, show_time: float = 10.0):
        ...

    @abc.abstractmethod
    def show_warning(self, title, info, show_time: float = 5.0):
        ...

    @abc.abstractmethod
    def show_rank(self, page: int, page_c: int,
                  rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]],
                  title: str = '排行榜'):
        ...

    @abc.abstractmethod
    def hide_msg_rank(self, update: bool = False):
        ...

    @abc.abstractmethod
    def show_loading(self, title: str):
        ...

    @abc.abstractmethod
    def stop_loading(self):
        ...

    @abc.abstractmethod
    def set_after_run(self, ms, func, *args):
        ...

    @abc.abstractmethod
    def update_control(self):
        ...

    @abc.abstractmethod
    def update_scan(self):
        ...

    @abc.abstractmethod
    def update_msg(self):
        ...

    @abc.abstractmethod
    def mainloop(self):
        ...

    @abc.abstractmethod
    def exit_win(self):
        ...


from . import station_event as tk_event


class GarbageStation(GarbageStationBase):
    """
    GarbageStation 垃圾站系统
    使用tkinter作为GUI
    """

    def set_after_run(self, ms, func, *args):  # 正常运行前设置定时任务 super.__init__可能会调用
        self.init_after_run_list.append((ms, func, args))

    def __conf_set_after_run(self):  # 配合 set_after_run 使用
        for ms, func, args in self.init_after_run_list:
            self.set_after_run_now(ms, func, *args)

    def set_after_run_now(self, ms, func, *args):  # 正常运行时设置定时任务
        self._window.after(ms, func, *args)

    def __init__(self,
                 db: DB,
                 cap: HGSCapture,
                 qr: HGSQRCoder,
                 aliyun: Aliyun,
                 loc: location_t = Config.base_location,
                 refresh_delay: int = Config.tk_refresh_delay):
        self.init_after_run_list: List[Tuple[int, Callable, Tuple]] = []

        super(GarbageStation, self).__init__(db, cap, qr, aliyun, loc)
        self.refresh_delay = refresh_delay

        self._window = tk.Tk()  # 系统窗口
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))  # 窗口高度
        self._win_width = int(self._sys_width * (2 / 3))  # 窗口宽度
        self._full_screen = False  # 是否全屏模式

        self.__conf_windows()

        self._cap_img = None  # 存储 PIL.image 的变量 防止gc释放
        self._cap_img_tk = None  # 存储 tkinter的image 的变量 防止gc释放
        self._user_im = None

        self._msg_time: Optional[float] = None  # msg 显示时间累计
        self._msg_show_time: float = 10.0
        self._disable_all_btn: bool = False  # 禁用所有按钮和操作

        self.__conf_font_size()  # 配置字体大小
        self.__create_tk()  # 创建组件
        self.__conf_tk()  # 配置组件

        self.__conf_after()
        self.__conf_set_after_run()
        self.__switch_to_no_user()

    def __create_tk(self):
        """
        创建tkinter组件
        该函数只被 __init__ 调用
        """
        self._title_label = tk.Label(self._window)  # 标题

        # 窗口操纵
        self._win_ctrl_button: List[tk.Button, tk.Button, tk.Button] = [tk.Button(self._window),
                                                                        tk.Button(self._window),
                                                                        tk.Button(self._window)]

        # 用户信息显示框
        win_info_type = Tuple[tk.Label, tk.Label, tk.Variable, str]
        self._user_frame = tk.Frame(self._window)
        self._user_name: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                          tk.StringVar(), "用户名")
        self._user_uid: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                         tk.StringVar(), "用户ID")
        self._user_score: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                           tk.StringVar(), "积分")
        self._user_rubbish: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                             tk.StringVar(), "垃圾量(7天)")
        self._user_eval: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                          tk.StringVar(), "垃圾分类信用")
        self._user_img = tk.Label(self._user_frame)

        # 扔垃圾相关按钮 (可回收, 不可回收, 有害垃圾, 厨余垃圾)
        self._throw_ctrl_frame = tk.Frame(self._window)
        self._throw_ctrl_btn: List[tk.Button] = [tk.Button(self._throw_ctrl_frame), tk.Button(self._throw_ctrl_frame),
                                                 tk.Button(self._throw_ctrl_frame), tk.Button(self._throw_ctrl_frame)]

        # 确认垃圾相关按钮 (通过, 不通过)
        self._check_ctrl_frame = tk.Frame(self._window)
        self._check_ctrl_btn: List[tk.Button] = [tk.Button(self._check_ctrl_frame), tk.Button(self._check_ctrl_frame)]

        # 系统信息显示框 (垃圾袋ID和当前时间)
        self._sys_info_frame = tk.Frame(self._window)
        self._garbage_id: win_info_type = (tk.Label(self._sys_info_frame), tk.Label(self._sys_info_frame),
                                           tk.StringVar(), "垃圾袋ID")
        self._sys_date: win_info_type = (tk.Label(self._sys_info_frame), tk.Label(self._sys_info_frame),
                                         tk.StringVar(), "系统时间")

        # 摄像头显示
        self._cap_label = tk.Label(self._window)
        self._cap_width = 0
        self._cap_height = 0

        # 用户操纵按钮
        self._user_btn_frame = tk.Frame(self._window)
        self._user_btn: List[tk.Button] = [tk.Button(self._user_btn_frame), tk.Button(self._user_btn_frame),
                                           tk.Button(self._user_btn_frame)]

        # 消息提示框
        self._msg_frame = tk.Frame(self._window)
        self._msg_line = tk.Label(self._msg_frame)
        self._msg_label: Tuple[tk.Label, tk.Text, tk.Variable] = (tk.Label(self._msg_frame),
                                                                  tk.Text(self._msg_frame),
                                                                  tk.StringVar())
        self._msg_y_scroll = tk.Scrollbar(self._msg_frame)
        self._msg_x_scroll = tk.Scrollbar(self._msg_frame)
        self._msg_hide = tk.Button(self._msg_frame)

        # 排行榜
        self._rank_frame = tk.Frame(self._window)
        self._rank_label = [tk.Label(self._rank_frame),
                            tk.Label(self._rank_frame),
                            tk.Label(self._rank_frame),
                            tk.Label(self._rank_frame),
                            tk.Label(self._rank_frame),
                            tk.Label(self._rank_frame)]
        self._rank_var = [tk.StringVar(),
                          tk.StringVar(),
                          tk.StringVar(),
                          tk.StringVar(),
                          tk.StringVar(),
                          tk.StringVar()]
        self._rank_btn = [tk.Button(self._rank_frame), tk.Button(self._rank_frame), tk.Button(self._rank_frame)]

        # 进度条
        self._loading_frame = tk.Frame(self._window)
        self._loading_line = tk.Label(self._loading_frame)
        self._loading_title: Tuple[tk.Label, tk.Variable] = tk.Label(self._loading_frame), tk.StringVar()
        self._loading_pro = ttk.Progressbar(self._loading_frame)

    def __conf_font_size(self, n: Union[int, float] = 1):
        """
        设置字体大小
        :param n: 缩放因子, 1为不缩放
        :return:
        """
        self._title_font_size = int(27 * n)  # 标题
        self._win_ctrl_font_size = int(15 * n)  # 控制按键
        self._win_info_font_size = int(18 * n)  # 用户信息
        self._throw_ctrl_btn_font_size = int(20 * n)  # 扔垃圾相关按钮
        self._check_ctrl_btn_font_size = int(20 * n)  # 检查垃圾相关按钮
        self._sys_info_font_size = int(18 * n)  # 系统信息
        self._user_btn_font_size = int(20 * n)  # 用户按键
        self._msg_font_size = int(20 * n)  # 消息提示框
        self._rank_font_title_size = int(24 * n)  # 排行榜标题
        self._rank_font_size = int(16 * n)  # 排行榜内容
        self._loading_tile_font = int(20 * n)  # 进度条

    def __conf_tk(self):
        """
        配置(绘制)窗口
        当切换全屏或启动界面时需要调用
        :return:
        """
        self.__conf_title_label()
        self.__conf_win_ctrl_button()
        self.__conf_user_info_label()
        self.__conf_throw_btn()
        self.__conf_check_btn()
        self.__conf_sys_info_label()
        self.__conf_cap_label()
        self.__conf_user_btn()
        self.__conf_msg()
        self.__conf_rank()
        self.__conf_loading()
        self.hide_msg_rank()  # 隐藏消息

    def __conf_windows(self):
        self._window.title('HGSSystem: Garbage Station')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = Config.tk_win_bg
        self._window.resizable(False, False)  # 禁止缩放
        self._window.protocol("WM_DELETE_WINDOW", lambda: self.show_exit())  # 设置标题栏[x]按钮
        self._window.overrideredirect(False)  # 显示标题栏

        # 快捷键相关配置
        def lock_windows(_):
            if self._disable_all_btn:
                return
            self.__set_windows_overrideredirect(True)

        def unlock_windows(_):
            if self._disable_all_btn:
                return
            if self.is_manager():
                self.__set_windows_overrideredirect(False)
                return
            self.show_warning("解锁窗口失败", f'用户不具备解锁窗口权限'.strip())

        def full_screen_windows(_):
            if self._disable_all_btn:
                return
            if not self._full_screen or self.is_manager():
                self.__full_screen(not self._full_screen)
                return
            self.show_warning("切换全屏失败", f'用户不具备切换全屏权限'.strip())

        def easter_eggs(_):
            if self._disable_all_btn:
                return
            self.easter_eggs()

        self._window.bind("<Alt-Control-KeyPress-s>", lock_windows)  # 锁定窗口
        self._window.bind("<Alt-Control-KeyPress-e>", unlock_windows)  # 解锁窗口
        self._window.bind("<F11>", full_screen_windows)  # 切换全屏
        self._window.bind("<F5>", easter_eggs)  # 触发彩蛋

    def __full_screen(self, full: bool = True):
        """
        切换全屏或非全屏
        计算缩放因子(窗口变大倍数)
        调用函数重绘窗口
        self.__conf_font_size
        self.__conf_tk
        :param full: True为切换至全屏, 否则切换至非全屏
        """
        self._window.attributes("-fullscreen", full)
        self._full_screen = full
        width = self._sys_width * (2 / 3)
        height = self._sys_height * (2 / 3)
        self._win_width = self._window.winfo_width()
        self._win_height = self._window.winfo_height()

        n = ((self._win_height / height) + (self._win_width / width)) / 2  # 平均放大倍数
        self.__conf_font_size(n)
        self.__conf_tk()

    def __set_windows_overrideredirect(self, show: bool = False):
        """
        :param show: True则显示标题栏, 否则不显示
        :return:
        """
        self._window.overrideredirect(show)

    def __conf_title_label(self):
        title_font = make_font(size=self._title_font_size, weight="bold")
        self._title_label['font'] = title_font
        self._title_label['bg'] = Config.tk_win_bg
        self._title_label['text'] = "HGSSystem: Garbage Station Control Center"  # 使用英语标题在GUI更美观
        self._title_label['anchor'] = 'w'
        self._title_label.place(relx=0.02, rely=0.01, relwidth=0.7, relheight=0.07)

    def __conf_win_ctrl_button(self):
        title_font = make_font(size=self._win_ctrl_font_size)

        for bt in self._win_ctrl_button:
            bt: tk.Button
            bt['font'] = title_font
            bt['bg'] = Config.tk_btn_bg

        rely = 0.02
        relwidth = 0.05
        relheight = 0.05

        bt_help: tk.Button = self._win_ctrl_button[0]
        bt_help['text'] = '帮助'
        bt_help['command'] = lambda: self.show_help_info()
        bt_help.place(relx=0.81, rely=rely, relwidth=relwidth, relheight=relheight)

        bt_about: tk.Button = self._win_ctrl_button[1]
        bt_about['text'] = '关于'
        bt_about['command'] = lambda: self.show_about_info()
        bt_about.place(relx=0.87, rely=rely, relwidth=relwidth, relheight=relheight)

        bt_exit: tk.Button = self._win_ctrl_button[2]
        bt_exit['text'] = '退出'
        bt_exit['command'] = lambda: self.show_exit()
        bt_exit.place(relx=0.93, rely=rely, relwidth=relwidth, relheight=relheight)

    def __conf_user_info_label(self):
        title_font = make_font(size=self._win_info_font_size - 1, weight="bold")
        info_font = make_font(size=self._win_info_font_size + 1)

        frame_width = self._win_width * 0.4  # frame宽度 (像素)
        frame_height = self._win_height * 0.4  # frame高度 (像素)
        bg_color = "#FA8072"  # 背景颜色

        self._user_frame['bg'] = bg_color
        self._user_frame['bd'] = 5
        self._user_frame['relief'] = "ridge"
        self._user_frame.place(relx=0.02, rely=0.1, relwidth=0.4, relheight=0.40)

        h_label = 5
        h_label_s = 1
        h_top = 2
        height_count = h_label * 5 + h_label_s * 4 + h_top * 2
        height_label = h_label / height_count
        height = h_top / height_count

        for lb_list in [self._user_score, self._user_rubbish, self._user_eval, self._user_name, self._user_uid]:
            lb_list[0]['font'] = title_font
            lb_list[0]['bg'] = bg_color
            lb_list[0]['fg'] = "#fffbf0"  # 字体颜色使用象牙白
            lb_list[0]['text'] = lb_list[3] + ":"
            lb_list[0]['anchor'] = 'e'
            lb_list[0].place(relx=0.0, rely=height, relwidth=0.35, relheight=height_label)
            height += height_label + h_label_s / height_count

        for lb_list in [self._user_score, self._user_rubbish, self._user_eval, self._user_name, self._user_uid]:
            lb_list[1]['font'] = info_font
            lb_list[1]['bg'] = bg_color
            lb_list[1]['fg'] = "#000000"  # 字体颜色使用纯黑
            lb_list[1]['textvariable'] = lb_list[2]
            lb_list[1]['anchor'] = 'w'
            lb_list[2].set('test')

        height = h_top / height_count
        for lb_list in [self._user_score, self._user_rubbish, self._user_eval]:
            lb_list[1].place(relx=0.36, rely=height, relwidth=0.19, relheight=height_label)
            height += height_label + h_label_s / height_count

        for lb_list in [self._user_name, self._user_uid]:
            lb_list[1].place(relx=0.36, rely=height, relwidth=0.63, relheight=height_label)
            height += height_label + h_label_s / height_count

        # 显示一张图片 (GUI更美观)
        img_relwidth = 0.30
        img_relheight = height_label * 3 + (h_label_s / height_count) * 2
        img = (Image.open(Config.picture_d['head']).
               resize((int(img_relwidth * frame_width), int(img_relheight * frame_height))))
        self._user_im = ImageTk.PhotoImage(image=img)
        self._user_img['image'] = self._user_im
        self._user_img.place(relx=1 - img_relwidth - 0.06, rely=0.09,
                             relwidth=img_relwidth, relheight=img_relheight)
        self._user_img['bd'] = 5
        self._user_img['relief'] = "ridge"

    def __conf_throw_btn(self):
        btn_font = make_font(size=self._throw_ctrl_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("可回收垃圾", "#00BFFF"),  # 按钮文字及其颜色
                                           ("其他垃圾", "#A9A9A9"),
                                           ("有害垃圾", "#DC143C"),
                                           ("厨余垃圾", "#32CD32")]

        self.__show_throw_frame()

        for btn, info in zip(self._throw_ctrl_btn, btn_info):
            btn['font'] = btn_font
            btn['bg'] = info[1]
            btn['text'] = info[0]

        self._throw_ctrl_btn[0]['command'] = lambda: self.throw_garbage(GarbageType.recyclable)
        self._throw_ctrl_btn[1]['command'] = lambda: self.throw_garbage(GarbageType.other)
        self._throw_ctrl_btn[2]['command'] = lambda: self.throw_garbage(GarbageType.hazardous)
        self._throw_ctrl_btn[3]['command'] = lambda: self.throw_garbage(GarbageType.kitchen)

        self._throw_ctrl_btn[0].place(relx=0.000, rely=0.000, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[1].place(relx=0.505, rely=0.000, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[2].place(relx=0.000, rely=0.505, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[3].place(relx=0.505, rely=0.505, relwidth=0.495, relheight=0.495)

    def __conf_check_btn(self):
        btn_font = make_font(size=self._check_ctrl_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("投放错误", "#ef7a82"),  # 按钮文字及其颜色
                                           ("投放正确", "#70f3ff")]

        self.__show_check_frame()

        for btn, info in zip(self._check_ctrl_btn, btn_info):
            btn['font'] = btn_font
            btn['text'] = info[0]
            btn['bg'] = info[1]

        self._check_ctrl_btn[0]['command'] = lambda: self.check_garbage(False)
        self._check_ctrl_btn[1]['command'] = lambda: self.check_garbage(True)

        self._check_ctrl_btn[0].place(relx=0.000, rely=0.000, relwidth=0.495, relheight=1)
        self._check_ctrl_btn[1].place(relx=0.505, rely=0.000, relwidth=0.495, relheight=1)

    def __conf_sys_info_label(self):
        title_font = make_font(size=self._sys_info_font_size - 1, weight="bold")
        info_font = make_font(size=self._sys_info_font_size + 1)

        bg_color = "#F0F8FF"
        self._sys_info_frame['bg'] = bg_color
        self._sys_info_frame['bd'] = 5
        self._sys_info_frame['relief'] = "ridge"
        self._sys_info_frame.place(relx=0.02, rely=0.51, relwidth=0.4, relheight=0.14)

        h_label = 5
        h_label_s = 1
        h_top = 2
        height_count = h_label * 2 + h_label_s * 1 + h_top * 2
        height_label = h_label / height_count

        height = h_top / height_count
        for info_list in [self._garbage_id, self._sys_date]:
            info_list[0]['font'] = title_font
            info_list[0]['bg'] = bg_color
            info_list[0]['anchor'] = 'e'
            info_list[0]['text'] = info_list[3] + ":"
            info_list[0].place(relx=0.0, rely=height, relwidth=0.35, relheight=height_label)
            height += height_label + h_label_s / height_count

        height = h_top / height_count
        for info_list in [self._garbage_id, self._sys_date]:
            info_list[1]['font'] = info_font
            info_list[1]['bg'] = bg_color
            info_list[1]['textvariable'] = info_list[2]
            info_list[1]['anchor'] = 'w'
            info_list[2].set('test')
            info_list[1].place(relx=0.36, rely=height, relwidth=0.63, relheight=height_label)
            height += height_label + h_label_s / height_count

    def __conf_user_btn(self):
        btn_font = make_font(size=self._user_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("详细信息", "#DDA0DD"),
                                           ("排行榜", "#B0C4DE"),
                                           ("搜索", "#F4A460")]

        self._user_btn_frame.place(relx=0.02, rely=0.66, relwidth=0.19, relheight=0.32)
        self._user_btn_frame['bg'] = Config.tk_win_bg

        """
        计算标签和间隔的大小比例(相对于Frame)
        标签和间隔的比例为5:1
        3个标签和2个间隔
        (h_label * 3 + h_label_s * 2) 表示 Frame 总大小
        height_label 标签相对于 Frame 的大小
        height_sep 间隔相对于 Frame 的大小
        """
        h_label = 5
        h_label_s = 1
        height_label = h_label / (h_label * 3 + h_label_s * 2)
        height_sep = h_label_s / (h_label * 3 + h_label_s * 2)

        height = 0
        for btn, info in zip(self._user_btn, btn_info):
            btn['font'] = btn_font
            btn['text'] = info[0]
            btn['bg'] = info[1]
            btn.place(relx=0.0, rely=height, relwidth=1.00, relheight=height_label)
            height += height_label + height_sep

        self._user_btn[0]['state'] = 'disable'  # 第一个按键默认为disable且点击无效果
        self._user_btn[1]['command'] = self.get_show_rank
        self._user_btn[2]['command'] = self.search_pic

    def __conf_cap_label(self):
        self._cap_label['bg'] = "#000000"
        self._cap_label['bd'] = 5
        self._cap_label['relief'] = "ridge"
        self._cap_width = int(self._win_width * 0.2)
        self._cap_height = int(self._win_height * 0.32)
        self._cap_label.place(relx=0.22, rely=0.66, relwidth=0.2, relheight=0.32)

    def __conf_msg(self):
        title_font = make_font(size=self._msg_font_size + 1, weight="bold")
        info_font = make_font(size=self._msg_font_size - 1)

        bg_color = Config.tk_second_win_bg
        self._msg_frame['bg'] = bg_color
        self._msg_frame['bd'] = 5
        self._msg_frame['relief'] = "ridge"
        # frame 不会立即显示

        self._msg_label[0]['font'] = title_font
        self._msg_label[0]['bg'] = bg_color
        self._msg_label[0]['anchor'] = 'w'
        self._msg_label[0]['textvariable'] = self._msg_label[2]

        self._msg_line['bg'] = '#000000'  # 分割线

        self._msg_label[1]['font'] = info_font
        self._msg_label[1]['bg'] = bg_color
        self._msg_label[1]['fg'] = '#000000'
        self._msg_label[1]['state'] = 'disable'
        self._msg_label[1]['bd'] = 0
        self._msg_label[1]['exportselection'] = False
        self._msg_label[1]['selectbackground'] = bg_color  # 被选中背景颜色和未选中颜色相同, 不启用选中
        self._msg_label[1]['selectforeground'] = '#000000'
        self._msg_label[1]['wrap'] = 'none'

        self._msg_y_scroll['orient'] = 'vertical'
        self._msg_y_scroll['command'] = lambda *args: (self.set_msg_time_now(), self._msg_label[1].yview(*args))
        self._msg_label[1]['yscrollcommand'] = lambda *args: (self.set_msg_time_now(), self._msg_y_scroll.set(*args))

        self._msg_x_scroll['orient'] = 'horizontal'
        self._msg_x_scroll['command'] = lambda *args: (self.set_msg_time_now(), self._msg_label[1].xview(*args))
        self._msg_label[1]['xscrollcommand'] = lambda *args: (self.set_msg_time_now(), self._msg_x_scroll.set(*args))

        self._msg_label[0].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.1)
        self._msg_line.place(relx=0.05, rely=0.15, relwidth=0.9, height=1)  # 一个像素的高度即可

        x_scroll = 0.03
        y_scroll = 0.02

        self._msg_label[1].place(relx=0.05, rely=0.20, relwidth=0.90 - y_scroll, relheight=0.64 - x_scroll)
        self._msg_x_scroll.place(relx=0.05, rely=0.84 - x_scroll, relwidth=0.90 - y_scroll, relheight=x_scroll)
        self._msg_y_scroll.place(relx=0.95 - y_scroll, rely=0.20, relwidth=y_scroll, relheight=0.64)

        self._msg_hide['font'] = info_font
        self._msg_hide['bg'] = Config.tk_btn_bg
        self._msg_hide['text'] = '关闭'
        self._msg_hide['command'] = lambda: self.hide_msg_rank(True)
        self._msg_hide.place(relx=0.42, rely=0.85, relwidth=0.16, relheight=0.09)

    def set_msg_time_now(self, show_time: Optional[float] = None):
        self._msg_time = time.time()
        if show_time is not None:
            self._msg_show_time = show_time

    def set_msg_time_none(self):
        self._msg_time = None

    def show_msg(self, title, info: str, msg_type='提示', big: bool = True, show_time: float = 10.0):
        if self._disable_all_btn:
            return

        self._msg_label[2].set(f'{msg_type}: {title}')

        self._msg_label[1]['state'] = 'normal'
        self._msg_label[1].delete(1.0, 'end')  # 删除所有元素
        for i in info.split('\n'):
            self._msg_label[1].insert('end', i + '\n')
        self._msg_label[1]['state'] = 'disable'

        if big:
            self._msg_frame.place(relx=0.45, rely=0.15, relwidth=0.53, relheight=0.70)
            self._check_ctrl_frame.place_forget()
            self._throw_ctrl_frame.place_forget()
            self._rank_frame.place_forget()
        else:
            self._msg_frame.place(relx=0.45, rely=0.20, relwidth=0.53, relheight=0.50)
            self.__show_check_frame()

            self._throw_ctrl_frame.place_forget()
            self._rank_frame.place_forget()

        self.set_msg_time_now(show_time)

    def show_warning(self, title, info, show_time: float = 5.0):
        self.show_msg(title, info, msg_type='警告', show_time=show_time)

    def __conf_rank(self):
        title_font = make_font(size=self._rank_font_title_size, weight="bold")
        info_font = make_font(size=self._rank_font_size)
        btn_font = make_font(size=self._msg_font_size - 1)

        bg_color = "#F5F5DC"
        self._rank_frame['bg'] = bg_color
        self._rank_frame['relief'] = "ridge"
        self._rank_frame['bd'] = 5
        # frame 不会立即显示

        self._rank_label[0]['font'] = title_font
        self._rank_label[0]['bg'] = bg_color
        self._rank_label[0]['textvariable'] = self._rank_var[0]
        self._rank_label[0].place(relx=0.02, rely=0.00, relwidth=0.96, relheight=0.1)

        for lb, v in zip(self._rank_label[1:], self._rank_var[1:]):
            lb['font'] = info_font
            lb['bg'] = "#F5FFFA"
            lb['textvariable'] = v
            lb['relief'] = "ridge"
            lb['bd'] = 2

        # 标签结束的高度为 0.12 + 0.15 * 5 = 0.87
        for btn, text in zip(self._rank_btn, ("上一页", "关闭", "下一页")):
            btn['font'] = btn_font
            btn['bg'] = Config.tk_btn_bg
            btn['text'] = text

        self._rank_btn[0].place(relx=0.050, rely=0.88, relwidth=0.25, relheight=0.08)
        self._rank_btn[0]['command'] = lambda: self.get_rank(-1)

        self._rank_btn[1].place(relx=0.375, rely=0.88, relwidth=0.25, relheight=0.08)
        self._rank_btn[1]['command'] = lambda: self.hide_msg_rank(True)

        self._rank_btn[2].place(relx=0.700, rely=0.88, relwidth=0.25, relheight=0.08)
        self._rank_btn[2]['command'] = lambda: self.get_rank(+1)

    def __set_rank_info(self, rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]]):
        """
        显示排行榜信息
        :param rank_info: 排行榜信息, 共计五个元组, 元组包含: 排名, uid, name, 分数, 评分
        :return:
        """
        if len(rank_info) > 5:
            rank_info = rank_info[:5]

        for lb in self._rank_label[1:]:  # 隐藏全部标签
            lb.place_forget()

        height = 0.12
        for i, info in enumerate(rank_info):
            no, name, uid, score, eval_, color = info
            self._rank_var[i + 1].set(f"NO.{no}  {name}\n\n"  # 中间空一行 否则中文字体显得很窄
                                      f"ID: {uid[0:Config.show_uid_len]}  "
                                      f"信用: {eval_} 积分: {score}")
            if color is None:
                self._rank_label[i + 1]['bg'] = "#F5FFFA"
            else:
                self._rank_label[i + 1]['bg'] = color

            self._rank_label[i + 1].place(relx=0.04, rely=height, relwidth=0.92, relheight=0.13)
            height += 0.15

    def show_rank(self, page: int, page_c: int,
                  rank_info: List[Tuple[int, uname_t, uid_t, score_t, score_t, Optional[str]]],
                  title: str = '排行榜'):
        if self._disable_all_btn:
            return

        self._rank_var[0].set(f'{title} ({page}/{page_c})')
        self._rank_frame.place(relx=0.47, rely=0.15, relwidth=0.47, relheight=0.80)
        frame_width = self._win_width * 0.53

        for lb in self._rank_label[1:]:
            lb['wraplength'] = frame_width * 0.85 - 5  # 设定自动换行的像素

        if page == 1:
            self._rank_btn[0]['state'] = 'disable'
        else:
            self._rank_btn[0]['state'] = 'normal'
        if page == page_c:
            self._rank_btn[2]['state'] = 'disable'
        else:
            self._rank_btn[2]['state'] = 'normal'

        self.__set_rank_info(rank_info)
        self._throw_ctrl_frame.place_forget()
        self._check_ctrl_frame.place_forget()
        self._msg_frame.place_forget()
        self.set_msg_time_none()

    def hide_msg_rank(self, update: bool = False):
        self.__show_check_frame()  # rank会令此消失
        self.__show_throw_frame()  # rank和msg令此消失
        self._msg_frame.place_forget()
        self._rank_frame.place_forget()
        self.set_msg_time_none()
        if update:
            self.update_user_time()

    def __conf_loading(self):
        title_font = make_font(size=self._loading_tile_font, weight="bold")

        self._loading_frame['bg'] = Config.tk_second_win_bg
        self._loading_frame['bd'] = 5
        self._loading_frame['relief'] = "ridge"
        # frame 不会立即显示

        self._loading_title[0]['font'] = title_font
        self._loading_title[0]['bg'] = Config.tk_second_win_bg
        self._loading_title[0]['anchor'] = 'w'
        self._loading_title[0]['textvariable'] = self._loading_title[1]
        self._loading_title[0].place(relx=0.02, rely=0.00, relwidth=0.96, relheight=0.6)

        self._loading_line['bg'] = '#000000'
        self._loading_line.place(relx=0.02, rely=0.6, relwidth=0.96, height=1)  # 一个像素的高度即可

        self._loading_pro['mode'] = 'indeterminate'  # 来回显示
        self._loading_pro['orient'] = 'horizontal'  # 横向进度条
        self._loading_pro['maximum'] = 100
        self._loading_pro.place(relx=0.02, rely=0.73, relwidth=0.96, relheight=0.22)

    def show_loading(self, title: str):
        self.set_all_btn_disable()
        self._loading_title[1].set(f"加载: {title}")
        self._loading_pro['value'] = 0
        self._loading_frame.place(relx=0.30, rely=0.40, relwidth=0.40, relheight=0.15)
        self._loading_pro.start(50)

    def stop_loading(self):
        self._loading_frame.place_forget()
        self._loading_pro.stop()
        self.set_reset_all_btn()

    def search_pic(self, img: Image = None):
        if img is None:
            img = self._cap_img
        super(GarbageStation, self).search_pic(img)

    def __show_check_frame(self):
        self._check_ctrl_frame.place(relx=0.45, rely=0.82, relwidth=0.53, relheight=0.16)

    def __show_throw_frame(self):
        self._throw_ctrl_frame.place(relx=0.45, rely=0.1, relwidth=0.53, relheight=0.70)

    def __define_after(self, ms, func, *args):
        self._window.after(ms, self.__after_func_maker(func), *args)

    def __conf_after(self):
        self.__define_after(self.refresh_delay, self.update_time)
        self.__define_after(self.refresh_delay, self.update_control)
        self.__define_after(self.refresh_delay, self.update_scan)
        self.__define_after(self.refresh_delay, self.update_msg)

    def __after_func_maker(self, func):
        def new_func(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:  # 捕获未考虑的错误
                self.show_msg("系统错误", "运行时产生了错误...", "错误", show_time=3.0)
                traceback.print_exc()
            finally:
                self._window.after(self.refresh_delay, new_func)

        return new_func

    def update_time(self):
        var: tk.Variable = self._sys_date[2]
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        var.set(f"{t}")

    def update_control(self):
        name: tk.Variable = self._user_name[2]
        uid: tk.Variable = self._user_uid[2]
        score: tk.Variable = self._user_score[2]
        rubbish: tk.Variable = self._user_rubbish[2]
        eval_: tk.Variable = self._user_eval[2]

        user_info: Dict[str, str] = self.get_user_info_no_update()
        if user_info.get('uid') is None:
            name.set('未登录')
            uid.set('未登录')
            eval_.set('---')
            rubbish.set('---')
            score.set('---')
            self.__switch_to_no_user()
        elif user_info.get('manager', '0') == '1':
            name.set(user_info.get('name'))
            uid_get = user_info.get('uid', None)
            if uid_get is None or len(uid_get) < 32:
                uid.set('error')
            else:
                uid.set(uid_get[0:21])
            eval_.set('管理员')
            rubbish.set('无')
            score.set('无')
            self.__switch_to_manager_user()
        else:
            name.set(user_info.get('name'))
            uid_get = user_info.get('uid', None)
            if uid_get is None or len(uid_get) < 32:
                uid.set('error')
            else:
                uid.set(uid_get[0:Config.show_uid_len])
            eval_.set(user_info.get('reputation'))
            rubbish.set(user_info.get('rubbish'))
            score.set(user_info.get('score'))
            self.__switch_to_normal_user()

        garbage = self.get_garbage()
        if garbage is None:
            self._garbage_id[2].set('---')
        else:
            gid = garbage.get_gid()
            if len(gid) > 20:
                gid = gid[-20:]
            self._garbage_id[2].set(gid)

    def update_scan(self):
        self.scan()

        # 需要存储一些数据 谨防被gc释放
        _cap_img_info = (Image.fromarray(cv2.cvtColor(self.get_cap_img(), cv2.COLOR_BGR2RGB)).
                         transpose(Image.FLIP_LEFT_RIGHT))
        self._cap_img = _cap_img_info

        img_width, img_height = _cap_img_info.size
        proportion = max(self._cap_width / img_width, self._cap_height / img_height)  # 缩放倍数, 取较大的那个
        new_width = int(img_width * proportion)
        new_height = int(img_height * proportion)
        _cap_img_info = _cap_img_info.resize((new_width, new_height), Image.ANTIALIAS)

        crop = (int(new_width / 2 - self._cap_width / 2),  # 左
                int(new_height / 2 - self._cap_height / 2),  # 上
                int(new_width / 2 + self._cap_width / 2),  # 右
                int(new_height / 2 + self._cap_height / 2))  # 下
        _cap_img_info = _cap_img_info.crop(crop)  # 裁剪图片

        self._cap_img_tk = ImageTk.PhotoImage(image=_cap_img_info)
        self._cap_label['image'] = self._cap_img_tk

    def update_msg(self):
        if self._msg_time is None:
            return

        if time.time() - self._msg_time > self._msg_show_time:  # 自动关闭消息
            self.hide_msg_rank()

    def __switch_to_normal_user(self):
        if self._disable_all_btn:
            return

        self.normal_user_disable()
        self.normal_user_able()

    def __switch_to_manager_user(self):
        if self._disable_all_btn:
            return

        self.manager_user_disable()
        self.manager_user_able()

    def __switch_to_no_user(self):
        self.manager_user_disable()
        self.normal_user_disable()
        self._user_btn[0]['state'] = 'disable'

    def normal_user_disable(self):
        set_tk_disable_from_list(self._check_ctrl_btn, flat='disable')
        self._user_btn[0]['state'] = 'normal'
        self._user_btn[0]['command'] = lambda: self.show_user_info()

    def manager_user_disable(self):
        set_tk_disable_from_list(self._throw_ctrl_btn, flat='disable')
        self._user_btn[0]['state'] = 'normal'
        self._user_btn[0]['command'] = lambda: self.show_garbage_info()

    def normal_user_able(self):
        set_tk_disable_from_list(self._throw_ctrl_btn, flat='normal')

    def manager_user_able(self):
        set_tk_disable_from_list(self._check_ctrl_btn, flat='normal')

    def set_all_btn_disable(self):
        self.__switch_to_no_user()  # 禁用所有操作性按钮
        self.hide_msg_rank()
        set_tk_disable_from_list(self._user_btn, flat='disable')
        set_tk_disable_from_list(self._win_ctrl_button, flat='disable')
        self._disable_all_btn = True

    def set_reset_all_btn(self):
        set_tk_disable_from_list(self._user_btn, flat='normal')
        set_tk_disable_from_list(self._win_ctrl_button, flat='normal')
        self.update_control()  # 位于_user_btn之后, 会自动设定detail按钮
        self._disable_all_btn = False

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()
