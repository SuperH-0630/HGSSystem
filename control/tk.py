import time
import conf
import cv2
import sys
import traceback
import tkinter as tk
import tkinter.font as font
from tool.type_ import *
import datetime
from PIL import Image, ImageTk
from control import Control, global_control, ControlScanType, ControlNotLogin, ThrowGarbageError, CheckGarbageError
from core.user import User, UserNotSupportError
from core.garbage import GarbageBag, GarbageType, GarbageBagNotUse


class GarbageStationException(Exception):
    ...


class GarbageStationStatus:
    status_normal = 1
    status_get_garbage_type = 2
    status_get_garbage_check = 3

    def __init__(self, win, ctrl: Control = global_control):
        self._win: GarbageStation = win
        self._ctrl = ctrl
        self._garbage: Optional[GarbageBag] = None
        self._flat = GarbageStationStatus.status_normal

    def to_get_garbage_type(self, garbage: GarbageBag):
        self._flat = GarbageStationStatus.status_get_garbage_type
        self.set_garbage(garbage)

    def to_get_garbage_check(self, garbage: GarbageBag):
        self._flat = GarbageStationStatus.status_get_garbage_check
        self.set_garbage(garbage)

    def set_garbage(self, garbage: GarbageBag):
        self._garbage = garbage

    def get_garbage(self) -> Optional[GarbageBag]:
        if not self._ctrl.check_user():
            self._garbage = None
        return self._garbage

    def get_user_info_no_update(self):
        return self._ctrl.get_user_info_no_update()

    def scan(self):
        return self._ctrl.scan()

    def get_cap_img(self):
        return self._ctrl.get_cap_img()

    def switch_user(self, user: User):
        return self._ctrl.switch_user(user)

    def throw_garbage(self, garbage_type: enum):
        if self._flat != GarbageStationStatus.status_get_garbage_type or self._garbage is None:
            self._win.show_warning("Operation Fail", "You should login first and scan the QR code of the trash bag")
            return

        try:
            self._ctrl.throw_garbage(self._garbage, garbage_type)
        except (ThrowGarbageError, UserNotSupportError, ControlNotLogin):
            self._win.show_warning("Operation Fail", "The garbage bags have been used.")
            raise
        finally:
            self._flat = GarbageStationStatus.status_normal
            self._garbage = None

    def check_garbage(self, check: bool):
        if self._flat != GarbageStationStatus.status_get_garbage_check or self._garbage is None:
            self._win.show_warning("Operation Fail", "You should login first and scan the QR code of the trash bag")
            return

        try:
            self._ctrl.check_garbage(self._garbage, check)
        except (ThrowGarbageError, UserNotSupportError, CheckGarbageError, GarbageBagNotUse):
            self._win.show_warning("Operation Fail", "The garbage bag has been checked")
        finally:
            self._flat = GarbageStationStatus.status_normal
            self._garbage = None

    def show_garbage_info(self):
        if self._flat != GarbageStationStatus.status_get_garbage_check or self._garbage is None:
            self._win.show_warning("Operation Fail", "You should login first and scan the QR code of the trash bag")
            return

        if not self._garbage.is_use():
            self._win.show_warning("Operation Fail", "The garbage bag has not been used")
            return

        info = self._garbage.get_info()
        garbage_type = GarbageType.GarbageTypeStrList[int(info['type'])]
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(info['use_time'])))
        self._win.show_msg("Garbage Info", (f"Type is {garbage_type}\n"
                                            f"Location:\n  {info['loc']}\n"
                                            f"Date:\n  {time_str}"))

    def show_user_info(self):
        if not self._ctrl.check_user():
            self._win.show_warning("Operation Fail", "You should login first")
            return

        info = self._ctrl.get_user_info()
        if info.get('manager', '0') == '1':
            self._win.show_msg("About User", (f"Manager User\n"
                                              f"UserName: {info['name']}\n"
                                              f"UserID:\n  {info['uid']}"))
        else:
            self._win.show_msg("About User", (f"Normal User\n"
                                              f"UserName: {info['name']}\n"
                                              f"UserID:\n  {info['uid']}\n"
                                              f"Score: {info['score']}\n"
                                              f"Reputation: {info['reputation']}\n"
                                              f"Rubbish: {info['rubbish']}"))

    def show_help_info(self):
        self._win.show_msg("Help", f'''
HGSSystem:
  1) Scan User QR code
  2) Scan Garbage QR code
  3) Select the type of garbage
  4) Garbage submitted successfully
     (You can leave now)
  5) Waiting for feedback
        '''.strip())

    def show_about_info(self):
        self._win.show_msg("About", f'''
HGSSystem (c) SuperHuan
HGSSystem is Garbage Sorting System
Author: SongZihuan[SuperHuan]
Run on python {sys.version}
                '''.strip())

    def show_exit(self):
        if self._ctrl.is_manager():
            self._win.exit_win()
            return
        self._win.show_warning("Exit", f'Permission not permitted'.strip())

    def is_manager(self):
        return self._ctrl.is_manager()


class GarbageStation:
    def __init__(self, ctrl: Control = global_control, refresh_delay: int = conf.tk_refresh_delay):
        self.refresh_delay = refresh_delay
        self._status = GarbageStationStatus(self, ctrl)

        self._window = tk.Tk()
        self._sys_height = self._window.winfo_screenheight()
        self._sys_width = self._window.winfo_screenwidth()

        self._win_height = int(self._sys_height * (2 / 3))
        self._win_width = int(self._sys_width * (2 / 3))
        self._full_screen = False

        self.__conf_windows()

        self._cap_img = None  # 存储 PIL.image 的变量 防止gc释放
        self._user_im = None

        self._msg_time = None  # msg 显示时间累计

        self.__creat_tk()
        self.__conf_tk()

        self.__conf_after()
        self.__switch_to_no_user()

    def __creat_tk(self):
        self.__conf_font_size()
        self._title_label = tk.Label(self._window)

        self._win_ctrl_button: Tuple[tk.Button, tk.Button, tk.Button] = (tk.Button(self._window),
                                                                         tk.Button(self._window),
                                                                         tk.Button(self._window))

        win_info_type = Tuple[tk.Label, tk.Label, tk.Variable, str]
        self._user_frame = tk.Frame(self._window)
        self._user_name: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                          tk.StringVar(), "UserName")
        self._user_uid: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                         tk.StringVar(), "UserID")
        self._user_score: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                           tk.StringVar(), "Score")
        self._user_rubbish: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                             tk.StringVar(), "Garbage")
        self._user_eval: win_info_type = (tk.Label(self._user_frame), tk.Label(self._user_frame),
                                          tk.StringVar(), "Evaluation")
        self._user_img = tk.Label(self._user_frame)

        self._throw_ctrl_frame = tk.Frame(self._window)
        self._throw_ctrl_btn: List[tk.Button] = [tk.Button(self._throw_ctrl_frame), tk.Button(self._throw_ctrl_frame),
                                                 tk.Button(self._throw_ctrl_frame), tk.Button(self._throw_ctrl_frame)]

        self._check_ctrl_frame = tk.Frame(self._window)
        self._check_ctrl_btn: List[tk.Button] = [tk.Button(self._check_ctrl_frame), tk.Button(self._check_ctrl_frame)]

        self._sys_info_frame = tk.Frame(self._window)
        self._garbage_id: win_info_type = (tk.Label(self._sys_info_frame), tk.Label(self._sys_info_frame),
                                           tk.StringVar(), "GID")
        self._sys_date: win_info_type = (tk.Label(self._sys_info_frame), tk.Label(self._sys_info_frame),
                                         tk.StringVar(), "Date")

        self._cap_label = tk.Label(self._window)

        self._user_btn_frame = tk.Frame(self._window)
        self._user_btn: List[tk.Button] = [tk.Button(self._user_btn_frame), tk.Button(self._user_btn_frame),
                                           tk.Button(self._user_btn_frame)]

        self._msg_frame = tk.Frame(self._window)
        self._msg_table = tk.Label(self._msg_frame), tk.Label(self._msg_frame), tk.StringVar(), tk.StringVar()
        self._msg_hide = tk.Button(self._msg_frame)

    def __conf_font_size(self, n: Union[int, float] = 1):
        self._title_font_size = int(25 * n)
        self._win_ctrl_font_size = int(15 * n)
        self._win_info_font_size = int(18 * n)
        self._throw_ctrl_btn_font_size = int(20 * n)
        self.__check_ctrl_btn_font_size = int(20 * n)
        self._sys_info_font_size = int(18 * n)
        self._user_btn_font_size = int(20 * n)
        self.__msg_font_size = int(20 * n)

    def __conf_tk(self):
        self.__conf_title_label()
        self.__conf_win_ctrl_button()
        self.__conf_user_info_label()
        self.__conf_throw_btn()
        self.__conf_check_btn()
        self.__conf_sys_info_label()
        self.__conf_cap_label()
        self.__conf_user_btn()
        self.__conf_msg()
        self.hide_msg()  # 隐藏消息

    def __conf_windows(self):
        self._window.title('HGSSystem: Garbage Station')
        self._window.geometry(f'{self._win_width}x{self._win_height}')
        self._window['bg'] = "#F0FFF0"  # 蜜瓜绿
        self._window.attributes("-topmost", True)
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", lambda: self._status.show_exit())
        self._window.overrideredirect(False)  # 显示标题栏
        self._window.bind("<Alt-Control-KeyPress-s>", lambda _: self.__set_windows_overrideredirect(True))  # 锁定窗口

        def unlock_windows(_):
            if self._status.is_manager():
                self.__set_windows_overrideredirect(False)
                return
            self.show_warning("Exit", f'Permission not permitted'.strip())

        def full_screen_windows(_):
            if not self._full_screen or self._status.is_manager():
                self.__full_screen(not self._full_screen)
                return
            self.show_warning("Exit", f'Permission not permitted'.strip())

        self._window.bind("<Alt-Control-KeyPress-s>", lambda _: self.__set_windows_overrideredirect(True))  # 锁定窗口
        self._window.bind("<Alt-Control-KeyPress-e>", unlock_windows)
        self._window.bind("<F11>", full_screen_windows)

    def __full_screen(self, full: bool = True):
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
        self._window.overrideredirect(show)

    def __conf_title_label(self):
        title_font = self.__make_font(size=self._title_font_size, weight="bold")
        self._title_label['font'] = title_font
        self._title_label['bg'] = "#F0FFF0"  # 蜜瓜绿
        self._title_label['text'] = "HGSSystem: GarbageStation Control Center"
        self._title_label['anchor'] = 'w'
        self._title_label.place(relx=0.02, rely=0.0, relwidth=0.6, relheight=0.07)

    def __conf_win_ctrl_button(self):
        title_font = self.__make_font(size=self._win_ctrl_font_size)

        for bt in self._win_ctrl_button:
            bt: tk.Button
            bt['font'] = title_font
            bt['bg'] = "#B0C4DE"  # 浅钢青

        bt_help: tk.Button = self._win_ctrl_button[0]
        bt_help['text'] = 'Help'
        bt_help['command'] = lambda: self._status.show_help_info()
        bt_help.place(relx=0.81, rely=0.01, relwidth=0.05, relheight=0.05)

        bt_about: tk.Button = self._win_ctrl_button[1]
        bt_about['text'] = 'About'
        bt_about['command'] = lambda: self._status.show_about_info()
        bt_about.place(relx=0.87, rely=0.01, relwidth=0.05, relheight=0.05)

        bt_exit: tk.Button = self._win_ctrl_button[2]
        bt_exit['text'] = 'Exit'
        bt_exit['command'] = lambda: self._status.show_exit()
        bt_exit.place(relx=0.93, rely=0.01, relwidth=0.05, relheight=0.05)

    def __conf_user_info_label(self):
        title_font = self.__make_font(size=self._win_info_font_size - 1, weight="bold")
        info_font = self.__make_font(size=self._win_info_font_size + 1)

        frame_width = self._win_width * 0.4
        frame_height = self._win_height * 0.4
        self._user_frame['bg'] = "#FA8072"
        self._user_frame.place(relx=0.02, rely=0.1, relwidth=0.4, relheight=0.40)
        self._user_frame['bd'] = 5
        self._user_frame['relief'] = "ridge"

        h_label = 5
        h_label_s = 1
        h_top = 2
        height_count = h_label * 5 + h_label_s * 4 + h_top * 2
        height_label = h_label / height_count
        height = h_top / height_count

        for lb_list in [self._user_score, self._user_rubbish, self._user_eval, self._user_name, self._user_uid]:
            lb_list[0]['font'] = title_font
            lb_list[0]['bg'] = "#FA8072"
            lb_list[0]['fg'] = "#FFB6C1"
            lb_list[0]['text'] = lb_list[3] + " " * (10 - len(lb_list[3])) + " :"
            lb_list[0]['anchor'] = 'e'
            lb_list[0].place(relx=0.0, rely=height, relwidth=0.35, relheight=height_label)
            height += height_label + h_label_s / height_count

        for lb_list in [self._user_score, self._user_rubbish, self._user_eval, self._user_name, self._user_uid]:
            lb_list[1]['font'] = info_font
            lb_list[1]['bg'] = "#FA8073"
            lb_list[1]['fg'] = "#000000"
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

        img_relwidth = 0.30
        img_relheight = height_label * 3 + (h_label_s / height_count) * 2
        img = (Image.open(conf.pic_d['head']).
               resize((int(img_relwidth * frame_width), int(img_relheight * frame_height))))
        self._user_im = ImageTk.PhotoImage(image=img)
        self._user_img['image'] = self._user_im
        self._user_img.place(relx=1 - img_relwidth - 0.06, rely=0.09,
                             relwidth=img_relwidth, relheight=img_relheight)
        self._user_img['bd'] = 5
        self._user_img['relief'] = "ridge"

    def __conf_throw_btn(self):
        btn_font = self.__make_font(size=self._throw_ctrl_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("Recyclable", "#00BFFF"),
                                           ("Other", "#A9A9A9"),
                                           ("Hazardous", "#DC143C"),
                                           ("Kitchen", "#32CD32")]

        self._throw_ctrl_frame.place(relx=0.45, rely=0.1, relwidth=0.53, relheight=0.70)

        for btn, info in zip(self._throw_ctrl_btn, btn_info):
            btn['font'] = btn_font
            btn['bg'] = info[1]
            btn['text'] = info[0]

        self._throw_ctrl_btn[0]['command'] = lambda: self._status.throw_garbage(GarbageType.recyclable)
        self._throw_ctrl_btn[1]['command'] = lambda: self._status.throw_garbage(GarbageType.other)
        self._throw_ctrl_btn[2]['command'] = lambda: self._status.throw_garbage(GarbageType.hazardous)
        self._throw_ctrl_btn[3]['command'] = lambda: self._status.throw_garbage(GarbageType.kitchen)

        self._throw_ctrl_btn[0].place(relx=0.000, rely=0.000, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[1].place(relx=0.505, rely=0.000, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[2].place(relx=0.000, rely=0.505, relwidth=0.495, relheight=0.495)
        self._throw_ctrl_btn[3].place(relx=0.505, rely=0.505, relwidth=0.495, relheight=0.495)

    def __conf_check_btn(self):
        btn_font = self.__make_font(size=self.__check_ctrl_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("Fail", "#ef7a82"),
                                           ("Pass", "#70f3ff")]

        self._check_ctrl_frame.place(relx=0.45, rely=0.82, relwidth=0.53, relheight=0.16)

        for btn, info in zip(self._check_ctrl_btn, btn_info):
            btn['font'] = btn_font
            btn['text'] = info[0]
            btn['bg'] = info[1]

        self._check_ctrl_btn[0]['command'] = lambda: self._status.check_garbage(False)
        self._check_ctrl_btn[1]['command'] = lambda: self._status.check_garbage(True)

        self._check_ctrl_btn[0].place(relx=0.000, rely=0.000, relwidth=0.495, relheight=1)
        self._check_ctrl_btn[1].place(relx=0.505, rely=0.000, relwidth=0.495, relheight=1)

    def __conf_sys_info_label(self):
        title_font = self.__make_font(size=self._sys_info_font_size - 1, weight="bold")
        info_font = self.__make_font(size=self._sys_info_font_size + 1)

        self._sys_info_frame['bg'] = "#F0F8FF"
        self._sys_info_frame.place(relx=0.02, rely=0.51, relwidth=0.4, relheight=0.14)
        self._sys_info_frame['bd'] = 5
        self._sys_info_frame['relief'] = "ridge"

        h_label = 5
        h_label_s = 1
        h_top = 2
        height_count = h_label * 2 + h_label_s * 1 + h_top * 2
        height_label = h_label / height_count

        height = h_top / height_count
        for info_list in [self._garbage_id, self._sys_date]:
            info_list[0]['font'] = title_font
            info_list[0]['bg'] = "#F0F8FF"
            info_list[0]['anchor'] = 'e'
            info_list[0]['text'] = info_list[3] + " " * (10 - len(info_list[3])) + " :"
            info_list[0].place(relx=0.0, rely=height, relwidth=0.35, relheight=height_label)
            height += height_label + h_label_s / height_count

        height = h_top / height_count
        for info_list in [self._garbage_id, self._sys_date]:
            info_list[1]['font'] = info_font
            info_list[1]['bg'] = "#F0F8FF"
            info_list[1]['textvariable'] = info_list[2]
            info_list[1]['anchor'] = 'w'
            info_list[2].set('test')
            info_list[1].place(relx=0.36, rely=height, relwidth=0.63, relheight=height_label)
            height += height_label + h_label_s / height_count

    def __conf_user_btn(self):
        btn_font = self.__make_font(size=self._user_btn_font_size, weight="bold")
        btn_info: List[Tuple[str, str]] = [("Detail", "#b0a4e3"),
                                           ("Ranking", "#b0a4e3"),
                                           ("Search", "#b0a4e3")]

        self._user_btn_frame.place(relx=0.02, rely=0.66, relwidth=0.19, relheight=0.32)
        self._user_btn_frame['bg'] = "#F0FFF0"

        h_label = 5
        h_label_s = 1
        height_count = h_label * 3 + h_label_s * 2
        height_label = h_label / (h_label * 3 + h_label_s * 2)

        height = 0
        for btn, info in zip(self._user_btn, btn_info):
            btn['font'] = btn_font
            btn['text'] = info[0]
            btn['bg'] = info[1]
            btn.place(relx=0.0, rely=height, relwidth=1.00, relheight=height_label)
            height += height_label + h_label_s / height_count

    def __conf_cap_label(self):
        self._cap_label['bg'] = "#000000"
        self._cap_label.place(relx=0.22, rely=0.66, relwidth=0.2, relheight=0.32)

    def __conf_msg(self):
        title_font = self.__make_font(size=self.__msg_font_size + 1, weight="bold")
        info_font = self.__make_font(size=self.__msg_font_size - 1)

        self._msg_frame['bg'] = "#F5FFFA"
        self._msg_frame['bd'] = 5
        self._msg_frame['relief'] = "ridge"
        # frame 不会立即显示

        self._msg_table[0]['font'] = title_font
        self._msg_table[0]['bg'] = "#F5FFFA"
        self._msg_table[0]['anchor'] = 'w'
        self._msg_table[0]['textvariable'] = self._msg_table[2]

        self._msg_table[1]['font'] = info_font
        self._msg_table[1]['bg'] = "#F5FFFA"
        self._msg_table[1]['anchor'] = 'nw'
        self._msg_table[1]['justify'] = 'left'
        self._msg_table[1]['textvariable'] = self._msg_table[3]

        self._msg_table[0].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.1)
        self._msg_table[1].place(relx=0.075, rely=0.2, relwidth=0.85, relheight=0.64)

        self._msg_hide['font'] = info_font
        self._msg_hide['bg'] = "#00CED1"
        self._msg_hide['text'] = 'Hide-Msg'
        self._msg_hide['command'] = lambda: self.hide_msg()
        self._msg_hide.place(relx=0.375, rely=0.85, relwidth=0.25, relheight=0.1)

    def show_msg(self, title, info, msg_type='info'):
        self._msg_table[2].set(f'{msg_type}: {title}')
        self._msg_table[3].set(f'{info}')
        self._msg_frame.place(relx=0.45, rely=0.20, relwidth=0.49, relheight=0.50)
        frame_width = self._win_width * 0.49
        self._msg_table[1]['wraplength'] = frame_width * 0.85 - 5  # 设定自动换行的像素
        self._throw_ctrl_frame.place_forget()
        self._msg_time = time.time()

    def show_warning(self, title, info):
        self.show_msg(title, info, msg_type='Warning')

    def hide_msg(self):
        self._msg_table[2].set('')
        self._msg_table[3].set('')
        self._throw_ctrl_frame.place(relx=0.45, rely=0.1, relwidth=0.53, relheight=0.70)
        self._msg_frame.place_forget()
        self._msg_time = None

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
                self.show_msg("System Exception", "Run Error...", "Error")
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

        user_info: Dict[str, str] = self._status.get_user_info_no_update()
        if user_info.get('uid') is None:
            name.set('Not-Login')
            uid.set('Not-Login')
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
            eval_.set('Manager-User')
            rubbish.set('Manager-User')
            score.set('Manager-User')
            self.__switch_to_manager_user()
        else:
            name.set(user_info.get('name'))
            uid_get = user_info.get('uid', None)
            if uid_get is None or len(uid_get) < 32:
                uid.set('error')
            else:
                uid.set(uid_get[0:21])
            eval_.set(user_info.get('reputation'))
            rubbish.set(user_info.get('rubbish'))
            score.set(user_info.get('score'))
            self.__switch_to_normal_user()

        garbage = self._status.get_garbage()
        if garbage is None:
            self._garbage_id[2].set('---')
        else:
            gid = garbage.get_gid()
            if len(gid) > 20:
                gid = gid[-20:]
            self._garbage_id[2].set(gid)

    def update_scan(self):
        res: Tuple[enum, any] = ControlScanType.no_to_done, None
        try:
            res = self._status.scan()
        except ControlNotLogin:
            self.show_warning("Scan Fail", "You should login first")

        # 需要存储一些数据 谨防被gc释放
        _cap_img_info = (Image.fromarray(cv2.cvtColor(self._status.get_cap_img(), cv2.COLOR_BGR2RGB)).
                         transpose(Image.FLIP_LEFT_RIGHT))
        self._cap_img = ImageTk.PhotoImage(image=_cap_img_info)
        self._cap_label['image'] = self._cap_img

        if res[0] == ControlScanType.switch_user:
            self._status.switch_user(res[1])
            self.update_control()
        elif res[0] == ControlScanType.throw_garbage:
            self._status.to_get_garbage_type(res[1])
            self.hide_msg()  # 如果有msg也马上隐藏
            self.update_control()
        elif res[0] == ControlScanType.check_garbage:
            self._status.to_get_garbage_check(res[1])
            self._status.show_garbage_info()  # 显示信息
            self.update_control()

    def update_msg(self):
        if self._msg_time is None:
            return

        if time.time() - self._msg_time > 10:  # 10s 自动关闭消息
            self.hide_msg()

    def __switch_to_normal_user(self):
        self.normal_user_disable()
        self.normal_user_able()

    def __switch_to_manager_user(self):
        self.manager_user_disable()
        self.manager_user_disable()

    def __switch_to_no_user(self):
        self.manager_user_disable()
        self.normal_user_disable()
        self._user_btn[0]['state'] = 'disable'

    def normal_user_disable(self):
        for btn in self._check_ctrl_btn:
            btn['state'] = 'disabled'
        self._user_btn[0]['state'] = 'normal'
        self._user_btn[0]['command'] = lambda: self._status.show_user_info()

    def manager_user_disable(self):
        for btn in self._throw_ctrl_btn:
            btn['state'] = 'disabled'
        self._user_btn[0]['state'] = 'normal'
        self._user_btn[0]['command'] = lambda: self._status.show_garbage_info()

    def normal_user_able(self):
        for btn in self._throw_ctrl_btn:
            btn['state'] = 'normal'

    def manager_user_able(self):
        for btn in self._check_ctrl_btn:
            btn['state'] = 'normal'

    @staticmethod
    def __make_font(family: str = 'noto', **kwargs):
        return font.Font(family=conf.font_d[family], **kwargs)

    def mainloop(self):
        self._window.mainloop()

    def exit_win(self):
        self._window.destroy()


station = GarbageStation()
station.mainloop()
