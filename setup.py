import os
import sys
import time
import warnings

print("是否执行初始化程序?执行初始化程序会令你丢失所有数据.")
res = input("[Y/n]")
if res != 'Y':
    exit(0)

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
uid = create_uid("admin", admin_passwd)
cursor.execute(f"INSERT INTO user(UserID, Name, IsManager, Phone, Score, Reputation, CreateTime) "
               f"VALUES ('{uid}', 'admin', 1, '{admin_phone}', 10, 300, {mysql_time()});")
sql.commit()

print("是否伪造数据？")
if input("[Y/n]") != "Y":
    cursor.close()
    sql.close()
    exit(0)

# 伪造数据
# 只有执行setup时可以伪造数据, 目的是不希望在生产环境上允许伪造数据
# 不过这是个开源程序, 所以你完全可以绕开限制

import random
from tool.login import randomPassword

random_manager = []
random_normal = []
loc = ["LOC-A", "LOC-B", "LOC-C"]


def random_phone() -> str:
    r_phone = ""
    while len(r_phone) < 11:
        r_phone += f"{random.randint(0, 9)}"
    return r_phone


def random_time() -> str:
    r_time = time.time()
    r_h = random.randint(0, 4 * 24)
    r_time -= r_h * 60 * 60
    return mysql_time(r_time)


def random_time_double() -> tuple[str, str]:
    r_time2 = r_time1 = time.time()
    r_h1 = random.randint(0, 4 * 24)
    r_h2 = random.randint(0, 4 * 24)
    r_time1 -= min(r_h1, r_h2) * 60 * 60
    r_time2 -= max(r_h1, r_h2) * 60 * 60
    return mysql_time(r_time1), mysql_time(r_time2)


def random_user(r_name, r_passwd, r_phone, r_time, is_manager: int, cur):
    r_score = random.randint(0, 50000) / 100
    r_reputation = random.randint(5, 995)
    r_uid = create_uid(r_name, r_passwd)
    cur.execute(f"INSERT INTO user(UserID, Name, IsManager, Phone, Score, Reputation, CreateTime) "
                f"VALUES ('{r_uid}', '{r_name}', {is_manager}, '{r_phone}', {r_score}, {r_reputation}, {r_time});")
    if is_manager:
        random_manager.append(r_uid)
        print(f"管理员: {r_name} {r_passwd} {r_phone} {r_reputation} {r_score} {r_uid}")
    else:
        random_normal.append(r_uid)
        print(f"普通用户: {r_name} {r_passwd} {r_phone} {r_reputation} {r_score} {r_uid}")


def random_garbage_n(r_time, cur):
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat) VALUES ({r_time}, 0);")


def random_garbage_c(r_time, r_time2, cur):
    user = random.choice(random_normal)
    r_loc = random.choice(loc)
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat, UserID, UseTime, GarbageType, Location) "
                f"VALUES ({r_time}, 1, '{user}', {r_time2}, {random.randint(1, 4)}, '{r_loc}');")


def random_garbage_u(r_time, r_time2, cur):
    user = random.choice(random_normal)
    checker = random.choice(random_manager)
    r_loc = random.choice(loc)
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat, UserID, UseTime, GarbageType, Location, "
                f"CheckerID, CheckResult) "
                f"VALUES ({r_time}, 1, '{user}', {r_time2}, {random.randint(1, 4)}, '{r_loc}', "
                f"'{checker}', {random.randint(0, 1)});")


print("步骤1, 注册管理账户[输入q结束]:")
while True:
    name = input("输入用户名:")
    passwd = input("输入密码:")
    phone = input("输入手机号码[输入x表示随机]:")
    creat_time = input("是否随机时间[n=不随机 y=随机]:")
    if name == 'q' or passwd == 'q' or phone == 'q' or creat_time == 'q':
        break
    if phone == 'x':
        phone = random_phone()
    if creat_time == 'n':
        c_time = mysql_time()
    else:
        c_time = random_time()
    random_user(name, passwd, phone, c_time, 1, cursor)

print("步骤2, 注册普通账户[输入q结束]:")
while True:
    name = input("输入用户名:")
    passwd = input("输入密码:")
    phone = input("输入手机号码[输入x表示随机]:")
    creat_time = input("是否随机时间[n=不随机 y=随机]:")
    if name == 'q' or passwd == 'q' or phone == 'q' or creat_time == 'q':
        break
    if creat_time == 'n':
        c_time = mysql_time()
    else:
        c_time = random_time()
    if phone == 'x':
        phone = random_phone()
    random_user(name, passwd, phone, c_time, 0, cursor)

count = int(input("步骤3, 注册随机管理员账户[输入个数]:"))
while count > 0:
    name = randomPassword()[:5]
    passwd = randomPassword()
    phone = random_phone()
    c_time = random_time()
    random_user(name, passwd, phone, c_time, 1, cursor)
    count -= 1

count = int(input("步骤3, 注册随机普通账户[输入个数]:"))
while count > 0:
    name = randomPassword()[:5]
    passwd = randomPassword()
    phone = random_phone()
    c_time = random_time()
    random_user(name, passwd, phone, c_time, 0, cursor)
    count -= 1

count = int(input("步骤4, 注册随机已检查垃圾袋[输入个数]:"))
while count > 0:
    count -= 1
    c_time2, c_time1 = random_time_double()
    random_garbage_u(c_time1, c_time2, cursor)

count = int(input("步骤5, 注册随机待检查垃圾袋[输入个数]:"))
while count > 0:
    count -= 1
    c_time2, c_time1 = random_time_double()
    random_garbage_c(c_time1, c_time2, cursor)

count = int(input("步骤6, 注册随机未使用垃圾袋[输入个数]:"))
while count > 0:
    count -= 1
    c_time = random_time()
    random_garbage_n(c_time, cursor)

sql.commit()
cursor.close()
sql.close()
