from typing import Dict, Union, NewType

gid_t = NewType("gid_t", str)  # garbage bag id 类型
uid_t = NewType("uid_t", str)  # user id 类型

uname_t = NewType("uname_t", str)  # user name 类型
passwd_t = NewType("passwd_t", str)  # user password 类型

count_t = NewType("count_t", int)  # 计数类型 (垃圾计数)
score_t = NewType("score_t", int)  # 积分类型
location_t = NewType("location_t", str)
time_t = NewType("time_t", float)  # 时间类型
day_t = NewType("day_t", int)

enum = NewType("enum", int)  # 枚举类型
