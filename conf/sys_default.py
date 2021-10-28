class ConfigSecretRelease:
    passwd_salt = "HGSSystem"


class ConfUserRelease:
    default_score = 10
    default_reputation = 300

    max_rubbish_week = 34
    limit_rubbish_week = 50

    max_score = 500  # 积分上限为500分


class ConfigSystemRelease:
    base_location = "Guangdong-KZ"
    search_reset_time = 10  # 搜索间隔的时间
    about_info = f'''
HGSSystem is Garbage Sorting System

HGSSystem 版权归属 SuperHuan
作者: SongZihuan[SuperHuan]

项目托关于 Github 平台
    '''.strip()


class ConfigExportRelease:
    qr_show_uid_len = 12  # qr 码上展示uid的长度


class ConfigTkinterRelease:
    tk_refresh_delay = 50  # 延时任务的时间

    tk_show_uid_len = ConfigExportRelease.qr_show_uid_len  # tk 界面上展示uid的长度
    ranking_tk_show_uid_len = tk_show_uid_len  # tk ranking 界面上展示uid的长度

    tk_second_win_bg = "#fffffb"  # tkinter 第二窗口 标准颜色
    tk_win_bg = "#F0FFF0"  # tkinter 一般窗口 标准颜色 蜜瓜绿
    tk_btn_bg = "#dcdcdc"  # tkinter 按钮 标准颜色


ConfigTkinter = ConfigTkinterRelease
ConfigExport = ConfigExportRelease
ConfigSystem = ConfigSystemRelease
ConfUser = ConfUserRelease
ConfigSecret = ConfigSecretRelease
