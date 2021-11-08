from .args import p_args
from .conf import conf_args


class ConfigSecretRelease:
    """ 加密相关配置 """
    passwd_salt = p_args['app_secret']
    wtf_secret = p_args['app_secret']


class ConfUserRelease:
    """ 用户信息相关配置 """
    default_score = int(conf_args.get("default_score", 10))
    default_reputation = int(conf_args.get("default_reputation", 300))

    max_rubbish_week = int(conf_args.get("max_rubbish_week", 34))
    limit_rubbish_week = int(conf_args.get("limit_rubbish_week", 50))

    max_score = int(conf_args.get("max_score", 500))


class ConfigSystemRelease:
    """ 系统信息相关配置 """

    base_location = conf_args.get("base_location", "KZ")
    search_reset_time = int(conf_args.get("search_reset_time", 10))  # 搜索间隔的时间

    show_uid_len = int(conf_args.get("show_uid_len", 12))  # 展示uid的长度
    show_gid_len = int(conf_args.get("show_gid_len", 12))  # 展示gid的长度

    about_info = f'''
HGSSystem is Garbage Sorting System

HGSSystem 版权归属 SuperHuan
作者: SongZihuan[SuperHuan]

项目托关于 Github 平台
    '''.strip()


class ConfigSystemTest(ConfigSystemRelease):
    """ 系统信息相关配置 """

    search_reset_time = 1  # 搜索间隔的时间
    about_info = f'''
HGSSystem is Garbage Sorting System

HGSSystem 版权归属 SuperHuan
作者: SongZihuan[SuperHuan]

开发者模式
项目托关于 Github 平台
    '''.strip()


class ConfigTkinterRelease:
    """ tkinter 相关配置 """
    tk_refresh_delay = int(conf_args.get("tk_refresh_delay", 50))  # 延时任务的时间

    tk_zoom = int(conf_args.get("tk_zoom", 1))  # 文字缩放
    tk_second_win_bg = "#fffffb"  # tkinter 第二窗口 标准颜色
    tk_win_bg = "#F0FFF0"  # tkinter 一般窗口 标准颜色 蜜瓜绿
    tk_btn_bg = "#dcdcdc"  # tkinter 按钮 标准颜色


ConfigTkinter = ConfigTkinterRelease
ConfigSystem = ConfigSystemTest if p_args['run'] == 'test' else ConfigSystemRelease
ConfUser = ConfUserRelease
ConfigSecret = ConfigSecretRelease
