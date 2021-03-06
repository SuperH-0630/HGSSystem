"""
入口程序
包都按需导入, 不需要使用的模块则不会导入
因此安装过程可以选用不完整安装
但依赖模块都都是固定的
"""

import sys
import os

from conf import Config

app = None


def can_not_load(name):
    print(f"无法加载 {name} 系统, 该系统或其依赖可能不存在", file=sys.stderr)


def main():
    """
    入口程序
    :return:
    """

    if __name__ != "__main__" and Config.program != "website":
        print("运行程序出错", file=sys.stderr)
        exit(1)

    if Config.mysql_url is None or Config.mysql_name is None:
        print("请提供MySQL信息")
        sys.exit(1)

    program_name = Config.program
    if program_name == "setup":  # setup程序不需要数据库链接等操作
        __main = os.path.dirname(os.path.abspath(__file__))

        exe = list(os.path.split(sys.executable))
        exe[-1] = exe[-1].replace("pythonw", "python")
        exe = os.path.join(*exe)
        res = os.system(f"{exe} {os.path.join(__main, 'init.py')} "
                        f"--mysql_url={Config.mysql_url} "
                        f"--mysql_name={Config.mysql_name} "
                        f"--mysql_passwd={Config.mysql_passwd} "
                        f"--mysql_port={Config.mysql_port}  "
                        f"--program=setup")
        if res != 0:
            print("初始化程序加载失败, 请检查配置是否正确而", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    import pymysql  # 下面才需要使用 pymysql
    try:
        from sql.db import DB
        mysql = DB()
    except pymysql.Error:
        print("无法连接到 MySQL")
        sys.exit(1)

    if program_name == "garbage":
        from equipment.aliyun import Aliyun
        if Config.aliyun_key is None or Config.aliyun_secret is None:
            print("请提供Aliyun key信息")
            sys.exit(1)

        try:
            from equipment.scan import HGSCapture, HGSQRCoder
            import tk_ui.station as garbage_station
        except ImportError:
            can_not_load("垃圾站系统")
            sys.exit(1)

        aliyun = Aliyun()
        cap = HGSCapture()
        qr = HGSQRCoder(cap)
        station = garbage_station.GarbageStation(mysql, cap, qr, aliyun)
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
    elif program_name == "website":
        try:
            from app import creat_web, App
            from flask import Flask
            from app.views import register
        except ImportError:
            can_not_load("在线排行榜服务")
            sys.exit(1)

        global app
        if __name__ == "__main__":
            app = creat_web(mysql)  # 暴露 app 接口
            print("Waitress Web 服务启动 访问: http://127.0.0.1:8080/")
            app.run_waitress(host='0.0.0.0', port="8080")
        else:
            tmp = creat_web(mysql)  # 暴露 app 接口
            app = tmp.get_app()
    else:
        can_not_load(program_name)
        sys.exit(1)


main()
