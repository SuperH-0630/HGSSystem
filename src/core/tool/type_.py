from typing import Union, TypeAlias

gid_t: TypeAlias = str  # garbage bag id 类型
uid_t: TypeAlias = str  # user id 类型

uname_t: TypeAlias = str  # user name 类型
passwd_t: TypeAlias = str  # user password 类型

count_t: TypeAlias = int  # 计数类型 (垃圾计数)
score_t: TypeAlias = int  # 积分类型
location_t: TypeAlias = str
time_t: TypeAlias = float  # 时间类型
day_t: TypeAlias = int

enum: int  # 枚举类型
