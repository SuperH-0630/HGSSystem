"""
文件名: conf/__init__.py
配置文件
"""

from font.noto import noto_font
from picture import head_pic, rank_bg_pic
from args import p_args
from .equipment import ConfigCapture
from .sql import ConfigDatabase
from .aliyun import ConfigAliyun
from .sys_default import ConfigExport, ConfigSystem, ConfigSecret, ConfigTkinter, ConfUser


class Config(ConfigTkinter, ConfigSecret, ConfigSystem, ConfUser, ConfigExport,
             ConfigAliyun,
             ConfigDatabase,
             ConfigCapture):
    run_type = p_args.run[0]
    program = p_args.program[0]

    font_d = {"noto": noto_font}
    picture_d = {"head": head_pic, "rank_bg": rank_bg_pic}
