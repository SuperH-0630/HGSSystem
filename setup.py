import os
import sys
import warnings

try:
    __import__("pip")
except ImportError:
    warnings.warn("The pip not found")
    raise

__setup = os.path.dirname(os.path.abspath(__file__))


def check_import(package, pip):
    try:
        __import__(package)
    except ImportError:
        res = os.system(f"{sys.executable} -m pip install {pip}")
        if res != 0:
            print(f"{pip} 依赖安装失败")
            exit(1)


check_import("cv2", "opencv-python")  # 图像处理
check_import("qrcode", "qrcode")  # 二维码生成
check_import("pymysql", "PyMySQL")  # 连接 MySQL服务器
check_import("cryptography", "cryptography")  # 链接 MySQL 服务器时加密
check_import("flask", "Flask")  # 网页服务
check_import("PIL", "Pillow")  # 图片处理

import pymysql
import conf

mysql_url = conf.mysql_url
mysql_name = conf.mysql_name
mysql_passwd = conf.mysql_passwd

sql = pymysql.connect(user=mysql_name, password=mysql_passwd, host=mysql_url)
cursor = sql.cursor()
with open(os.path.join(__setup, "setup.sql"), "r", encoding='utf-8') as f:
    all_sql = f.read().split(';')
    for s in all_sql:
        if s.strip() == "":
            continue
        cursor.execute(f"{s};")
    sql.commit()

admin_passwd = input("Enter Admin Passwd: ")
admin_phone = ""
while len(admin_phone) != 11:
    admin_phone = input("Enter Admin Phone[len = 11]: ")

from tool.login import create_uid
from tool.time_ import mysql_time

# 生成基本 admin 用户
uid = create_uid("admin", admin_passwd, admin_phone)
cursor.execute(f"INSERT INTO user(UserID, Name, IsManager, Phone, Score, Reputation, CreateTime) "
               f"VALUES ('{uid}', 'admin', 1, '{admin_phone}', 10, 300, {mysql_time()});")
sql.commit()
cursor.close()
sql.close()
