from args import p_args


class ConfigSecretRelease:
    passwd_salt = p_args['app_secret']
    wtf_secret = p_args['app_secret']


class ConfUserRelease:
    default_score = 10
    default_reputation = 300

    max_rubbish_week = 34
    limit_rubbish_week = 50

    max_score = 500  # 积分上限为500分


class ConfigSystemRelease:
    base_location = "Guangdong-KZ"
    search_reset_time = 10  # 搜索间隔的时间
    show_uid_len = 12  # 展示uid的长度
    about_info = f'''
HGSSystem is Garbage Sorting System

HGSSystem 版权归属 SuperHuan
作者: SongZihuan[SuperHuan]

项目托关于 Github 平台
    '''.strip()


class ConfigSystemDebug(ConfigSystemRelease):
    search_reset_time = 1  # 搜索间隔的时间
    about_info = f'''
HGSSystem is Garbage Sorting System

HGSSystem 版权归属 SuperHuan
作者: SongZihuan[SuperHuan]

开发者模式
项目托关于 Github 平台
    '''.strip()


class ConfigTkinterRelease:
    tk_refresh_delay = 50  # 延时任务的时间

    tk_second_win_bg = "#fffffb"  # tkinter 第二窗口 标准颜色
    tk_win_bg = "#F0FFF0"  # tkinter 一般窗口 标准颜色 蜜瓜绿
    tk_btn_bg = "#dcdcdc"  # tkinter 按钮 标准颜色


ConfigTkinter = ConfigTkinterRelease
ConfigExport = ConfigExportRelease
ConfigSystem = ConfigSystemDebug if p_args['run'] == 'Debug' else ConfigSystemRelease
ConfUser = ConfUserRelease
ConfigSecret = ConfigSecretRelease
