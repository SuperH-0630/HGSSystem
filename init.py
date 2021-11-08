import os
import sys
import time
from typing import Union, List

print("初始化程序开始执行")
print("开始检查依赖")

print(r"是否使用 http://pypi.douban.com/simple/ 源")
use_i = input(r"[Y/n]")
if use_i == "Y" or use_i == 'y':
    use_i = r"-i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com"
else:
    use_i = ""

try:
    __import__("pip")
except ImportError:
    print("检查结束, 未找到pip")
    sys.exit(1)
else:
    print("依赖 pip 存在")
    if os.system(f"{sys.executable} -m pip install {use_i} --upgrade pip") != 0:
        print(f"依赖 pip 更新失败", file=sys.stderr)
    else:
        print(f"依赖 pip 更新成功")

__setup = os.path.dirname(os.path.abspath(__file__))


def check_import(packages: Union[str, List[str]], pips: Union[str, List[str]]):
    if type(pips) is str:
        pips = [pips]
    if type(packages) is str:
        packages = [packages]
    try:
        for package in packages:
            __import__(package)
            print(f"依赖 {package} 存在")
    except ImportError:
        for pip in pips:
            command = f"{sys.executable} -m pip install {use_i} {pip}"
            print(f"依赖 {pip} 安装: {command}")
            if os.system(command) != 0:
                print(f"依赖 {pip} 安装失败", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"依赖 {packages}:{pip} 安装成功")


check_import("cv2", "opencv-python==4.5.3.56")  # 图像处理
check_import("qrcode", "qrcode")  # 二维码生成
check_import("pymysql", "PyMySQL")  # 连接 MySQL服务器
check_import("cryptography", "cryptography")  # 链接 MySQL 服务器时加密
check_import("flask", "Flask")  # 网页服务
check_import("flask", "Flask")  # 网页服务
check_import("flask_wtf", "Flask-WTF")  # 网页服务
check_import("flask_login", "Flask-Login")  # 网页服务
check_import("pyecharts", "pyecharts")  # 网页服务
check_import("waitress", "waitress")  # waitress 网页服务
check_import("PIL", "Pillow")  # 图片处理
check_import("numpy", "numpy")  # matplotlib依赖
check_import("matplotlib", "matplotlib")  # matplotlib依赖

check_import(["oss2", "viapi", "aliyunsdkcore", "aliyunsdkimagerecog"],
             ["oss2", "aliyun-python-sdk-viapiutils", "viapi-utils", "aliyun-python-sdk-imagerecog"])  # 阿里云依赖

import pymysql
from conf import Config
from conf import p_args

mysql_url = Config.mysql_url
mysql_name = Config.mysql_name
mysql_passwd = Config.mysql_passwd
mysql_port = Config.mysql_port

try:
    print(f"MySQL -h {mysql_url} -u {mysql_name} -P {mysql_port} -p{mysql_passwd}")
    if mysql_port is None:
        mysql_port = 0
    else:
        mysql_port = int(mysql_port)
    sql = pymysql.connect(user=mysql_name, password=mysql_passwd, host=mysql_url, port=mysql_port)
    cursor = sql.cursor()
except pymysql.err.Error:
    print("请提供正确的MySQL信息", file=sys.stderr)
    sys.exit(1)

print("是否执行数据库初始化程序?\n执行初始化程序会令你丢失所有数据.")
res = input("[Y/n]")
if res == 'Y' or res == 'y':
    with open(os.path.join(__setup, "init.sql"), "r", encoding='utf-8') as f:
        all_sql = f.read().split(';\n')  # 使用 `;` 作为分隔符是不够的, 因为函数中可能会使用`;`表示语句
        for s in all_sql:
            if s.strip() == "":
                continue
            cursor.execute(f"{s};")
        sql.commit()

    admin_passwd = input("创建 'admin' 管理员的密码: ")
    admin_phone = ""
    while len(admin_phone) != 11:
        admin_phone = input("输入 'admin' 管理员的电话[长度=11]: ")

    from tool.login import create_uid
    from tool.time import mysql_time

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

check_import("faker", "Faker")  # matplotlib依赖
from faker import Faker

fake = Faker(locale='zh_CN')

random_manager = []
random_normal = []
loc = [fake.street_name() for _ in range(4)]


def random_time() -> str:
    r_time = int(time.time())
    r_start = int(r_time - 35 * 24 * 60 * 60)
    return mysql_time(random.randint(r_start, r_time))


def random_time_double() -> tuple[str, str]:
    r_time = int(time.time())
    r_start = int(r_time - 35 * 24 * 60 * 60)
    r_h1 = random.randint(r_start, r_time)
    r_h2 = random.randint(r_start, r_time)
    return mysql_time(min(r_h1, r_h2)), mysql_time(max(r_h1, r_h2))


def random_user(r_name, r_passwd, r_phone, r_time, is_manager: int, cur, c_g=0, u_g=0):
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
    while c_g > 0:
        c_g -= 1
        t2, t1 = random_time_double()
        random_garbage_c_to_user(r_uid, t1, t2, cur)

    while u_g > 0:
        u_g -= 1
        t2, t1 = random_time_double()
        random_garbage_u_to_user(r_uid, t1, t2, cur)


def random_garbage_n(r_time, cur):
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat) VALUES ({r_time}, 0);")


def random_garbage_c_to_user(user, r_time, r_time2, cur):
    r_loc = random.choice(loc)
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat, UserID, UseTime, GarbageType, Location) "
                f"VALUES ({r_time}, 1, '{user}', {r_time2}, {random.randint(1, 4)}, '{r_loc}');")


def random_garbage_u_to_user(user, r_time, r_time2, cur):
    checker = random.choice(random_manager)
    r_loc = random.choice(loc)
    cur.execute(f"INSERT INTO garbage(CreateTime, Flat, UserID, UseTime, GarbageType, Location, "
                f"CheckerID, CheckResult) "
                f"VALUES ({r_time}, 1, '{user}', {r_time2}, {random.randint(1, 4)}, '{r_loc}', "
                f"'{checker}', {random.randint(0, 1)});")


def random_garbage_c(r_time, r_time2, cur):
    user = random.choice(random_normal)
    random_garbage_c_to_user(user, r_time, r_time2, cur)


def random_garbage_u(r_time, r_time2, cur):
    user = random.choice(random_normal)
    random_garbage_c_to_user(user, r_time, r_time2, cur)


def random_news(c_time, cur):
    user = random.choice(random_normal)
    text = f"大家好，我是 {fake.name()}, 我居住在 {fake.street_name()}{fake.street_address()}, 谢谢"
    cur.execute(f"INSERT INTO context(Context, Author, Time) "
                f"VALUES ('{text}', '{user}', {c_time});")


def random_goods(cur):
    car = fake.license_plate()
    quantity = random.randint(0, 20)
    score = random.randint(10, 200)
    cur.execute(f"INSERT INTO goods(Name, Quantity, Score) "
                f"VALUES ('{car}', '{quantity}', {score});")


def make_fake():
    print("步骤1, 注册管理账户[输入q结束]:")
    while True:
        if (name := input("输入用户名:")) == 'q':  # 这里使用了海象表达式, 把赋值运算变成一种表达式
            break
        if (passwd := input("输入密码:")) == 'q':
            break
        if (phone := input("输入手机号码[输入x表示随机]:")) == 'q':
            break
        if (creat_time := input("是否随机时间[n=不随机 y=随机]:")) == 'q':
            break

        if phone == 'x':
            phone = fake.phone_number()
        if creat_time == 'n':
            c_time = mysql_time()
        else:
            c_time = random_time()
        random_user(name, passwd, phone, c_time, 1, cursor)

    print("步骤2, 注册普通账户[输入q结束]:")
    while True:
        if (name := input("输入用户名:")) == 'q':  # 这里使用了海象表达式, 把赋值运算变成一种表达式
            break
        if (passwd := input("输入密码:")) == 'q':
            break
        if (phone := input("输入手机号码[输入x表示随机]:")) == 'q':
            break
        if (creat_time := input("是否随机时间[n=不随机 y=随机]:")) == 'q':
            break
        if (w_garbage := input("待检测垃圾个数:")) == 'q':
            break
        if (c_garbage := input("已检测垃圾个数:")) == 'q':
            break

        if creat_time == 'n':
            c_time = mysql_time()
        else:
            c_time = random_time()

        if phone == 'x':
            phone = fake.phone_number()
        w_garbage = int(w_garbage)
        c_garbage = int(w_garbage)
        random_user(name, passwd, phone, c_time, 0, cursor, w_garbage, c_garbage)

    count = int(input("步骤3, 注册随机管理员账户[输入个数]:"))
    while count > 0:
        name = randomPassword()[:5]
        passwd = randomPassword()
        phone = fake.phone_number()
        c_time = random_time()
        random_user(name, passwd, phone, c_time, 1, cursor)
        count -= 1

    count = int(input("步骤3, 注册随机普通账户[输入个数]:"))
    while count > 0:
        name = randomPassword()[:5]
        passwd = randomPassword()
        phone = fake.phone_number()
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

    count = int(input("步骤7, 注册随机新闻内容:"))
    while count > 0:
        count -= 1
        c_time = random_time()
        random_news(c_time, cursor)

    count = int(input("步骤8, 注册随机商城内容:"))
    while count > 0:
        count -= 1
        random_goods(cursor)


make_fake()
sql.commit()
cursor.close()
sql.close()
