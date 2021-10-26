import csv

from . import DBBit
from .db import DB
from tool.type_ import *
from tool.login import create_uid, randomPassword
from tool.time_ import mysql_time
from core.user import NormalUser, ManagerUser, User
import conf
from . import garbage


def update_user_score(where: str, score: score_t, db: DB) -> int:
    if len(where) == 0 or score < 0:
        return -1

    cur = db.update(table="user", kw={"score": score}, where=where)
    if cur is None:
        return -1
    return cur.rowcount


def update_user_reputation(where: str, reputation: score_t, db: DB) -> int:
    if len(where) == 0 or reputation <= 1 or reputation >= 1000:
        return -1

    cur = db.update(table="user", kw={"Reputation": reputation}, where=where)
    if cur is None:
        return -1
    return cur.rowcount


def search_user_by_fields(columns, uid: uid_t, name: uname_t, phone: phone_t, db: DB):
    where = ""
    if uid is not None:
        where += f"UserID=‘{uid}’ AND "
    if name is not None:
        where += f"Name='{name}' AND "
    if phone is not None:
        where += f"Phone='{phone}' AND "

    if len(where) != 0:
        where = where[0:-4]  # 去除末尾的AND

    return search_from_user_view(columns, where, db)


def search_from_user_view(columns, where: str, db: DB):
    cur = db.search(columns=columns,
                    table="user",
                    where=where)
    if cur is None:
        return None
    result = cur.fetchall()
    re = []
    for res in result:
        n = [res[a] for a in range(5)]
        n.append("True" if res[5] == DBBit.BIT_1 else "False")
        re.append(n)
    return re


def find_user_by_id(uid: uid_t, db: DB) -> Optional[User]:
    cur = db.search(columns=["UserID", "Name", "IsManager", "Score", "Reputation"],
                    table="user",
                    where=f"UserID = '{uid}'")
    if cur is None or cur.rowcount == 0:
        return None
    assert cur.rowcount == 1
    res = cur.fetchone()
    assert len(res) == 5

    uid: uid_t = res[0]
    name: uname_t = str(res[1])
    manager: bool = res[2] == DBBit.BIT_1

    if manager:
        return ManagerUser(name, uid)
    else:
        score: score_t = res[3]
        reputation: score_t = res[4]
        rubbish: count_t = garbage.count_garbage_by_time(uid, db)
        return NormalUser(name, uid, reputation, rubbish, score)  # rubbish 实际计算


def find_user_by_name(name: uname_t, passwd: passwd_t, db: DB) -> Optional[User]:
    uid = create_uid(name, passwd)
    return find_user_by_id(uid, db)


def is_user_exists(uid: uid_t, db: DB) -> bool:
    cur = db.search(columns=["UserID"],
                    table="user",
                    where=f"UserID = '{uid}'")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def update_user(user: User, db: DB) -> bool:
    if not is_user_exists(user.get_uid(), db):
        return False

    uid = user.get_uid()
    info: Dict[str, str] = user.get_info()
    is_manager = info['manager']
    if is_manager == '1':
        cur = db.update(table="user",
                        kw={"IsManager": {is_manager}},
                        where=f"UserID = '{uid}'")
    else:
        score = info['score']
        reputation = info['reputation']
        cur = db.update(table="user",
                        kw={"IsManager": {is_manager},
                            "Score": {score},
                            "Reputation": {reputation}},
                        where=f"UserID = '{uid}'")
    return cur is not None


def create_new_user(name: Optional[uname_t], passwd: Optional[passwd_t], phone: phone_t,
                    manager: bool, db: DB) -> Optional[User]:
    if name is None:
        name = f'User-{phone[-6:]}'

    if passwd is None:
        passwd = randomPassword()

    if len(phone) != 11:
        return None

    uid = create_uid(name, passwd)
    if is_user_exists(uid, db):
        return None
    is_manager = '1' if manager else '0'
    cur = db.insert(table="user",
                    columns=["UserID", "Name", "IsManager", "Phone", "Score", "Reputation", "CreateTime"],
                    values=f"'{uid}', '{name}', {is_manager}, '{phone}', {conf.default_score}, "
                           f"{conf.default_reputation}, {mysql_time()}")
    if cur is None:
        return None
    if is_manager:
        return ManagerUser(name, uid)
    return NormalUser(name, uid, conf.default_reputation, 0, conf.default_score)


def get_user_phone(uid: uid_t, db: DB) -> Optional[str]:
    cur = db.search(columns=["Phone"], table="user", where=f"UserID = '{uid}'")
    if cur is None or cur.rowcount == 0:
        return None
    assert cur.rowcount == 1
    return cur.fetchall()[0]


def del_user(uid: uid_t, db: DB) -> bool:
    cur = db.search(columns=["GarbageID"], table="garbage_time", where=f"UserID = '{uid}'")  # 确保没有引用

    if cur is None or cur.rowcount != 0:
        return False
    cur = db.delete(table="user", where=f"UserID = '{uid}'")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_user_from_where_scan(where: str, db: DB) -> int:
    cur = db.search(columns=["UserID"], table="user", where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_user_from_where(where: str, db: DB) -> int:
    cur = db.search(columns=["GarbageID"], table="garbage_time", where=where)  # 确保没有引用
    if cur is None or cur.rowcount != 0:
        return False
    cur = db.delete(table="user", where=where)
    if cur is None:
        return -1
    return cur.rowcount


def creat_user_from_csv(path, db: DB) -> List[User]:
    res = []
    with open(path, "r") as f:
        reader = csv.reader(f)
        first = True
        name_index = 0
        passwd_index = 0
        phone_index = 0
        manager_index = 0
        for item in reader:
            if first:
                try:
                    name_index = item.index('Name')
                    passwd_index = item.index('Passwd')
                    phone_index = item.index('Phone')
                    manager_index = item.index('Manager')
                except (ValueError, TypeError):
                    return []
                first = False
                continue
            name = item[name_index]
            passwd = item[passwd_index]
            phone = item[phone_index]
            if item[manager_index].upper() == "TRUE":
                is_manager = True
            elif item[manager_index].upper() == "FALSE":
                is_manager = False
            else:
                continue
            user = create_new_user(name, passwd, phone, is_manager, db)
            if user is not None:
                res.append(user)
    return res


def creat_auto_user_from_csv(path, db: DB) -> List[User]:
    res = []
    with open(path, "r") as f:
        reader = csv.reader(f)
        first = True
        phone_index = 0
        for item in reader:
            if first:
                try:
                    phone_index = item.index('Phone')
                except (ValueError, TypeError):
                    return []
                first = False
                continue
            phone = item[phone_index]
            user = create_new_user(None, None, phone, False, db)
            if user is not None:
                res.append(user)
    return res
