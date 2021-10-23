from db import DB, DBBit
from tool.type_ import *
from tool.login import create_uid, randomPassword
from core.user import NormalUser, ManagerUser, User
import conf
from garbage import count_garbage_by_time


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
    if len(where) > 0:
        where = f"WHERE {where} "

    column = ", ".join(columns)
    cur = db.search(f"SELECT {column} FROM user_view {where};")
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
    cur = db.search(f"SELECT uid, name, manager, score, reputation FROM user WHERE uid = '{uid}';")
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
        rubbish: count_t = count_garbage_by_time(uid, db)
        return NormalUser(name, uid, reputation, rubbish, score)  # rubbish 实际计算


def find_user_by_name(name: uname_t, passwd: passwd_t, db: DB) -> Optional[User]:
    uid = create_uid(name, passwd)
    return find_user_by_id(uid, db)


def is_user_exists(uid: uid_t, db: DB) -> bool:
    cur = db.search(f"SELECT uid FROM user WHERE uid = '{uid}';")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def update_user(user: User, db: DB) -> bool:
    if not is_user_exists(user.get_uid(), db):
        return False

    uid = user.get_uid()
    info: dict = user.get_info()
    is_manager = info['manager']
    if is_manager == '1':
        cur = db.done(f"UPDATE user "
                      f"SET manager = {is_manager} "
                      f"WHERE uid = '{uid}';")
    else:
        score = info['score']
        reputation = info['reputation']
        cur = db.done(f"UPDATE user "
                      f"SET manager = {is_manager},"
                      f"    score = {score},"
                      f"    reputation = {reputation} "
                      f"WHERE uid = '{uid}';")
    return cur is not None


def create_new_user(name: Optional[uname_t], passwd: Optional[passwd_t], phone: phone_t,
                    manager: bool, db: DB) -> Optional[User]:
    if name is None:
        name = f'User-{phone[-6:]}'

    if passwd is None:
        passwd = randomPassword()

    uid = create_uid(name, passwd)
    if is_user_exists(uid, db):
        return None
    is_manager = '1' if manager else '0'
    cur = db.done(f"INSERT INTO user(uid, name, manager, phone, score, reputation) "
                  f"VALUES ('{uid}', '{name}', {is_manager}, '{phone}', {conf.default_score}, "
                  f"{conf.default_reputation});")
    if cur is None:
        return None
    if is_manager:
        return ManagerUser(name, uid)
    return NormalUser(name, uid, conf.default_reputation, 0, conf.default_score)


def get_user_phone(uid: uid_t, db: DB) -> Optional[str]:
    cur = db.done(f"SELECT phone FROM user WHERE uid = {uid};")
    if cur is None or cur.rowcount == 0:
        return None
    assert cur.rowcount == 1
    return cur.fetchall()[0]


def del_user(uid: uid_t, db: DB) -> bool:
    cur = db.search(f"SELECT gid FROM garbage_time WHERE uid = '{uid}';")  # 确保没有引用
    if cur is None or cur.rowcount != 0:
        return False
    cur = db.done(f"DELETE FROM user WHERE uid = '{uid}';")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_user_from_where_scan(where: str, db: DB) -> int:
    cur = db.search(f"SELECT uid FROM user WHERE {where};")
    print(f"SELECT uid FROM user WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_user_from_where(where: str, db: DB) -> int:
    cur = db.search(f"SELECT gid FROM garbage_time WHERE {where};")  # 确保没有引用
    if cur is None or cur.rowcount != 0:
        return False
    cur = db.done(f"DELETE FROM user WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


if __name__ == '__main__':
    mysql_db = DB()
    name_ = 'Huan12'
    usr = find_user_by_name(name_, "123", mysql_db)
    if usr is None:
        usr = create_new_user(name_, "123", "12345678900", False, mysql_db)
    print(usr)

    for i in range(9):
        usr.evaluate(False)
        print(usr)

    for i in range(1):
        usr.evaluate(True)
        print(usr)

    update_user(usr, mysql_db)
    usr = find_user_by_name(name_, "123", mysql_db)
    print(usr)
