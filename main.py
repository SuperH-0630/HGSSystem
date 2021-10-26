"""
入口程序
包都按需导入, 不需要使用的模块则不会导入
因此安装过程可以选用不完整安装
但依赖模块都都是固定的
"""

import sys

import conf
from conf.args import p_args

program_name = p_args.program[0]
if program_name == "setup":  # setup程序不需要数据库链接等操作
    import os
    import sys

    __main = os.path.dirname(os.path.abspath(__file__))
    res = os.system(f"{sys.executable} {os.path.join(__main, 'setup.py')} "
                    f"--mysql_url={conf.mysql_url} "
                    f"--mysql_name={conf.mysql_name} "
                    f"--mysql_passwd={conf.mysql_passwd} "
                    f"--program=setup")
    if res != 0:
        print("初始化程序加载失败", file=sys.stderr)
        exit(1)
    exit(0)

from sql.db import DB

mysql = DB()


def can_not_load(name):
    print(f"无法加载 {name} 模块, 该系统可能不存在", file=sys.stderr)


if program_name == "garbage":
    try:
        from equipment.scan import HGSCapture, HGSQRCoder
        import tk_ui.station as garbage_station
    except ImportError:
        can_not_load("垃圾站系统")
        sys.exit(1)

    cap = HGSCapture()
    qr = HGSQRCoder(cap)
    station = garbage_station.GarbageStation(mysql, cap, qr)
    station.mainloop()
elif program_name == "ranking":
    try:
        import tk_ui.ranking as ranking_station
    except ImportError:
        can_not_load("排行榜系统")
        sys.exit(1)

    station = ranking_station.RankingStation(mysql)
    station.mainloop()
elif program_name == "manager":
    try:
        import tk_ui.admin as admin_station
    except ImportError:
        can_not_load("管理员系统")
        sys.exit(1)

    station = admin_station.AdminStation(mysql)
    station.mainloop()
elif program_name == "ranking_website":
    try:
        from app import rank as rank_web
    except ImportError:
        can_not_load("在线排行榜服务")
        sys.exit(1)

    web, app = rank_web.creat_ranking_website(mysql)
    web.run()
else:
    can_not_load(program_name)
    sys.exit(1)
