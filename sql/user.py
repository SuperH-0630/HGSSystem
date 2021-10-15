from db import DB, mysql_db, DBBit
from tool.type_ import *
from tool.login import creat_uid, randomPassword
from core.user import NormalUser, ManagerUser, User
import conf
from .garbage import countGarbageByTime


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
        rubbish: count_t = countGarbageByTime(uid, db)
        return NormalUser(name, uid, reputation, rubbish, score)  # rubbish 实际计算


def find_user_by_name(name: uname_t, passwd: passwd_t, db: DB) -> Optional[User]:
    uid = creat_uid(name, passwd)
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


def creat_new_user(name: Optional[uname_t], passwd: Optional[passwd_t], phone: phone_t, manager: bool, db: DB) -> Optional[User]:
    if name is None:
        name = randomPassword()

    if passwd is None:
        passwd = randomPassword()

    uid = creat_uid(name, passwd)
    if is_user_exists(uid, db):
        return None
    is_manager = manager if '1' else '0'
    cur = db.done(f"INSERT INTO user(uid, name, manager, phone, score, reputation) "
                  f"VALUES ('{uid}', '{name}', {is_manager}, '{phone}', {conf.default_score}, "
                  f"{conf.default_reputation});")
    if cur is None:
        return None
    if is_manager:
        return ManagerUser(name, uid)
    return NormalUser(name, uid, conf.default_reputation, 0, conf.default_score)


if __name__ == '__main__':
    name_ = 'Huan8'
    usr = find_user_by_name(name_, "123", mysql_db)
    if usr is None:
        usr = creat_new_user(name_, "123", "12345678900", False, mysql_db)
    print(usr)

    for i in range(90):
        usr.evaluate(False)
        print(usr)

    for i in range(90):
        usr.evaluate(True)
        print(usr)

    update_user(usr, mysql_db)
    usr = find_user_by_name(name_, "123", mysql_db)
    print(usr)
