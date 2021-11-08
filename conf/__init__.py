"""
文件名: conf/__init__.py
配置文件
"""

from .conf import conf_args
from .font.noto import noto_font, noto_bold_font, noto_medium_font, noto_thin_font, noto_black_font, noto_regular_font
from .picture import head_pic, rank_bg_pic, logo_pic, logo_ico
from .args import p_args
from .equipment import ConfigCapture
from .sql import ConfigDatabase
from .aliyun import ConfigAliyun
from .sys_default import ConfigSystem, ConfigSecret, ConfigTkinter, ConfUser
from .matplotlib_conf import ConfigMatplotlib


class Config(ConfigTkinter, ConfigSecret, ConfigSystem, ConfUser,
             ConfigAliyun,
             ConfigDatabase,
             ConfigCapture,
             ConfigMatplotlib):
    run_type = p_args['run']
    program = p_args['program']

    font_d = {
        "noto": noto_font,
        "noto-bold": noto_bold_font,
        "noto-medium": noto_medium_font,
        "noto-thin": noto_thin_font,
        "noto-black": noto_black_font,
        "noto-regular": noto_regular_font
    }

    picture_d = {
        "head": head_pic,
        "rank_bg": rank_bg_pic,
        "logo": logo_pic,
        "logo-ico": logo_ico
    }
