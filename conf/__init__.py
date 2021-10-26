"""
文件名: conf/__init__.py
配置文件
"""

from font.noto import noto_font
from picture import head_pic, rank_bg_pic

from .equipment import *
from .sql import *
from .sys_default import *

font_d = {
    "noto": noto_font
}

picture_d = {
    "head": head_pic,
    "rank_bg": rank_bg_pic
}
