import time
from decimal import Decimal
from db import DB, DBBit, DBDataException, DBDoneException
from tool.type_ import *
from tool.time_ import HGSTime
from core.garbage import GarbageBag, GarbageType


class GarbageDBException(DBDataException):
    ...


def search_from_garbage_view(columns, where: str, db: DB):
    if len(where) > 0:
        where = f"WHERE {where} "

    column = ", ".join(columns)
    print(f"SELECT {column} FROM garbage_view {where};")
    cur = db.search(f"SELECT {column} FROM garbage_view {where};")
    if cur is None:
        return None
    res = cur.fetchall()
    return res


def count_garbage_by_time(uid: uid_t, db: DB):
    ti: time_t = time.time()
    start = ti - 3.5 * 24 * 60 * 60  # 前后3.5天
    end = ti + 3.5 * 24 * 60 * 60
    cur = db.search(f"SELECT gid FROM garbage_time WHERE uid = '{uid}' AND use_time BETWEEN {start} AND {end};")
    if cur is None:
        return -1
    return cur.rowcount


def __find_garbage(sql: str, res_len, db: DB):
    cur = db.search(sql)
    if cur is None or cur.rowcount == 0:
        return [None, tuple()]
    assert cur.rowcount == 1
    res = cur.fetchone()
    assert len(res) == res_len
    return GarbageBag(str(res[0])), res


def find_not_use_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    return __find_garbage(f"SELECT gid FROM garbage_n WHERE gid = {gid};", 1, db)[0]


def find_wait_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[int, bytes, Decimal, str, str]
    gb: GarbageBag
    gb, res = __find_garbage(f"SELECT gid, type, use_time, uid, loc FROM garbage_c WHERE gid = {gid};", 5, db)
    if gb is None:
        return None

    garbage_type: enum = int(res[1].decode())
    use_time: time_t = float(res[2])
    uid: uid_t = res[3]
    loc: location_t = res[4]

    gb.config_use(garbage_type, use_time, uid, loc)
    return gb


def find_use_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[int, bytes, Decimal, str, str, bytes]
    gb: GarbageBag
    gb, res = __find_garbage(f"SELECT gid, type, use_time, uid, loc, right_use, check_uid "
                             f"FROM garbage_u WHERE gid = {gid};", 7, db)
    if gb is None:
        return None

    garbage_type: enum = int(res[1].decode())
    use_time: time_t = float(res[2])
    uid: uid_t = res[3]
    loc: location_t = res[4]
    check: bool = res[5] == DBBit.BIT_1
    check_uid: uid_t = res[6]

    gb.config_use(garbage_type, use_time, uid, loc)
    gb.config_check(check, check_uid)
    return gb


def find_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[bool, int] = is_garbage_exists(gid, db)
    if not res[0]:
        return None
    elif res[1] == 0:
        re = find_not_use_garbage(gid, db)
    elif res[1] == 1:
        re = find_wait_garbage(gid, db)
    elif res[1] == 2:
        re = find_use_garbage(gid, db)
    else:
        re = None
    assert re is not None
    return re


def is_garbage_exists(gid: gid_t, db: DB) -> Tuple[bool, int]:
    cur = db.search(f"SELECT gid, flat FROM garbage WHERE gid = {gid};")
    if cur is None or cur.rowcount == 0:
        return False, 0
    assert cur.rowcount == 1
    res: Tuple[int, int] = cur.fetchone()
    return True, res[1]


def update_garbage(garbage: GarbageBag, db: DB) -> bool:
    re = find_garbage(garbage.get_gid(), db)
    if re is None:
        return False

    if re.is_use() and not garbage.is_use() or re.is_check()[0] and not garbage.is_check():
        return False

    if not garbage.is_use() and not garbage.is_check()[0]:
        return True  # 不做任何修改

    gid = garbage.get_gid()
    info = garbage.get_info()

    try:
        db.done_(f"DELETE FROM garbage_n WHERE gid = {gid};")
        db.done_(f"DELETE FROM garbage_c WHERE gid = {gid};")
        db.done_(f"DELETE FROM garbage_u WHERE gid = {gid};")

        if garbage.is_check()[0]:
            db.done_(f"UPDATE garbage SET flat = 2 WHERE gid = {gid};")
            db.done_(f"INSERT INTO garbage_u(gid, uid, use_time, type, loc, right_use, check_uid) "
                     f"VALUES ({info['gid']} , '{info['user']}'  , {info['use_time']}, {info['type']}, "
                     f"       '{info['loc']}', {info['check']}, '{info['checker']}');")
        else:
            db.done_(f"UPDATE garbage SET flat = 1 WHERE gid = {gid};")
            db.done_(f"INSERT INTO garbage_c(gid, uid, use_time, type, loc) "
                     f"VALUES ({info['gid']} , '{info['user']}', {info['use_time']}, {info['type']}, "
                     f"       '{info['loc']}');")
    except DBDoneException:
        return False
    finally:
        db.done_commit()
    return True


def creat_new_garbage(db: DB) -> Optional[GarbageBag]:
    cur = db.done("INSERT INTO garbage() VALUES ();")
    if cur is None:
        return None
    assert cur.rowcount == 1
    gid = cur.lastrowid
    cur = db.done(f"INSERT INTO garbage_n(gid) VALUES ({gid});")
    if cur is None:
        return None
    assert cur.rowcount == 1
    return GarbageBag(str(gid))


def del_garbage_core(gid: gid_t, db: DB, from_: str) -> bool:
    cur = db.done(f"DELETE FROM {from_} WHERE gid = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    cur = db.done(f"DELETE FROM garbage WHERE gid = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_not_use(gid: gid_t, db: DB) -> bool:
    return del_garbage_core(gid, db, "garbage_n")


def del_garbage_wait_check(gid: gid_t, db: DB) -> bool:
    return del_garbage_core(gid, db, "garbage_c")


def del_garbage_has_check(gid: gid_t, db: DB) -> bool:
    return del_garbage_core(gid, db, "garbage_u")


def del_garbage(gid, db: DB):
    res = del_garbage_not_use(gid, db)
    if res:
        return True
    res = del_garbage_wait_check(gid, db)
    if res:
        return True
    return del_garbage_has_check(gid, db)


def del_garbage_where_core(where, db: DB, from_: str, from_int: int) -> int:
    cur = db.done_(f"DELETE FROM {from_} WHERE {where};")
    if cur is None:
        return -1
    elif cur.rowcount == 0:
        return 0

    cur = db.done(f"DELETE FROM garbage WHERE flat={from_int} AND gid NOT IN (SELECT gid FROM {from_});")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_not_use(where, db: DB) -> int:
    return del_garbage_where_core(where, db, "garbage_n", 0)


def del_garbage_where_wait_check(where, db: DB) -> int:
    return del_garbage_where_core(where, db, "garbage_c", 1)


def del_garbage_where_has_check(where, db: DB) -> int:
    return del_garbage_where_core(where, db, "garbage_u", 2)


def del_garbage_where_scan_core(where, db: DB, from_: str) -> int:
    cur = db.done(f"SELECT gid FROM {from_} WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_not_use(where, db: DB) -> int:
    return del_garbage_where_scan_core(where, db, "garbage_n")


def del_garbage_where_scan_wait_check(where, db: DB) -> int:
    return del_garbage_where_scan_core(where, db, "garbage_c")


def del_garbage_where_scan_has_check(where, db: DB) -> int:
    return del_garbage_where_scan_core(where, db, "garbage_u")


def del_all_garbage(db: DB) -> int:
    cur = db.done(f"DELETE FROM garbage_u WHERE 1;")
    if cur is None:
        return -1
    cur = db.done(f"DELETE FROM garbage_c WHERE 1;")
    if cur is None:
        return -1
    cur = db.done(f"DELETE FROM garbage_n WHERE 1;")
    if cur is None:
        return -1
    cur = db.done(f"DELETE FROM garbage WHERE 1;")
    if cur is None:
        return -1
    return cur.rowcount


def del_all_garbage_scan(db: DB) -> int:
    cur = db.done(f"SELECT gid FROM garbage WHERE 1;")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_not_use_many(gid_from: gid_t, gid_to: gid_t, db: DB) -> int:
    cur = db.done(f"DELETE FROM garbage "
                  f"WHERE gid IN (SELECT gid FROM garbage_n WHERE gid BETWEEN {gid_from} and {gid_to});")
    if cur is None or cur.rowcount == 0:
        return 0
    cur = db.done(f"DELETE FROM garbage WHERE gid BETWEEN {gid_from} and {gid_to};")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.rowcount


if __name__ == '__main__':
    mysql_db = DB()
    bag = creat_new_garbage(mysql_db)
    print(bag)
    bag.config_use(GarbageType.recyclable, HGSTime(), "1e1d30a1f9b78c8fa852d19b4cfaee79", "HuaDu")
    update_garbage(bag, mysql_db)
    print(bag)

    bag = find_garbage(bag.get_gid(), mysql_db)
    print(bag)

    bag.config_check(True, "048529ca5c6accf594b74e6f73ee1bf0")
    update_garbage(bag, mysql_db)
    print(bag)

    bag = find_garbage(bag.get_gid(), mysql_db)
    print(bag)

    print(count_garbage_by_time("1e1d30a1f9b78c8fa852d19b4cfaee79", mysql_db))
