"""
文件名: conf/__init__.py
配置文件
"""

import sys
import warnings
from font.noto import noto_font
from picture import *

if len(sys.argv) != 4:
    warnings.warn(f"参数不足: {len(sys.argv)}")
    raise exit(1)

MYSQL_URL = sys.argv[1]
MYSQL_NAME = sys.argv[2]
MYSQL_PASSWORD = sys.argv[3]

passwd_salt = "HGSSystem"
default_score = 10
default_reputation = 300

max_rubbish_week = 34
limit_rubbish_week = 50

base_location = "Guangdong-Guangzhou"

font_d = {
    "noto": noto_font
}

pic_d = {
    "head": head_pic,
    "rank_bg": rank_bg_pic
}

capture_num = 0  # 摄像头号
capture_arg = []

tk_refresh_delay = 50  # 延时任务的时间

qr_show_uid_len = 12  # qr 码上展示uid的长度
tk_show_uid_len = qr_show_uid_len  # tk 界面上展示uid的长度
ranking_tk_show_uid_len = tk_show_uid_len  # tk ranking 界面上展示uid的长度

tk_win_bg = "#fffffb"  # tkinter manager 窗口 按钮标准颜色
tk_btn_bg = "#dcdcdc"  # tkinter 按钮 按钮标准颜色

about_info = f'''
HGSSystem (c) SuperHuan
From github
HGSSystem is Garbage Sorting System
Author: SongZihuan[SuperHuan]
'''.strip()
