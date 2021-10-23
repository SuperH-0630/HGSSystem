import time
from db import DB, DBBit, DBDataException, DBDoneException
from tool.type_ import *
from tool.time_ import HGSTime, mysql_time, time_from_mysql
from core.garbage import GarbageBag, GarbageType


class GarbageDBException(DBDataException):
    ...


def update_garbage_type(where: str, type_: int, db: DB) -> int:
    if len(where) == 0:
        return -1

    cur = db.done(f"UPDATE garbage SET GarbageType={type_} WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def update_garbage_check(where: str, check_: bool, db: DB) -> int:
    if len(where) == 0:
        return -1

    i = 1 if check_ else 0
    cur = db.done(f"UPDATE garbage SET CheckResult={i} WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def __get_time(time_str: str) -> float:
    if time_str == 'now':
        return time.time()
    if time_str.startswith("Date:") and len(time_str) >= 5:
        return time_from_mysql(time_str[5:])
    return float(time_str)


def __get_time_diff(time_str: str) -> float:
    if time_str.endswith("s") and len(time_str) >= 2:
        return float(time_str[:-1])
    elif time_str.endswith("ms") and len(time_str) >= 3:
        return float(time_str[:-1]) / 1000
    elif time_str.endswith("min") and len(time_str) >= 4:
        return float(time_str[:-1]) * 60
    elif time_str.endswith("h") and len(time_str) >= 2:
        return float(time_str[:-1]) * 60 * 60
    elif time_str.endswith("d") and len(time_str) >= 2:
        return float(time_str[:-1]) * 24 * 60 * 60
    return float(time_str)


def __search_fields_time(time_: str, time_name: str) -> str:
    if time_ == '<=now':
        return f"{time_name}<={mysql_time()} AND"
    sp = time_.split(',')
    if len(sp) == 2:
        try:
            time_list = __get_time(sp[0]), __get_time(sp[1])
            a = min(time_list)
            b = max(time_list)
        except (TypeError, ValueError):
            return ""
        else:
            return f"({time_name} BETWEEN {mysql_time(a)} AND {mysql_time(b)}) AND"
    sp = time_.split(';')
    if len(sp) == 2:
        try:
            time_list = __get_time(sp[0]), __get_time_diff(sp[1])
            a = time_list[0] - time_list[1]
            b = time_list[0] + time_list[1]
        except (TypeError, ValueError):
            return ""
        else:
            return f"({time_name} BETWEEN {mysql_time(a)} AND {mysql_time(b)}) AND"
    try:
        t = __get_time(time_)
    except (TypeError, ValueError):
        return ""
    else:
        return f"({time_name}={mysql_time(t)} AND"


def search_garbage_by_fields(columns, gid, uid, cuid, create_time, use_time, loc, type_, check, db: DB):
    where = ""
    if gid is not None:
        where += f"GarbageID={gid} AND "
    if uid is not None:
        where += f"UserID=‘{uid}’ AND "
    if cuid is not None:
        where += f"CheckerID='{cuid}' AND "
    if loc is not None:
        where += f"Location='{loc}' AND "
    if check is not None:
        if check == "False":
            where += f"CheckResult=0 AND "
        else:
            where += f"CheckResult=1 AND "
    if type_ is not None and type_ in GarbageType.GarbageTypeStrList:
        res = GarbageType.GarbageTypeStrList.index(type_)
        where += f"Phone={res} AND "
    if create_time is not None:
        where += __search_fields_time(create_time, "CreateTime")
    if use_time is not None:
        where += __search_fields_time(use_time, "UseTime")

    if len(where) != 0:
        where = where[0:-4]  # 去除末尾的AND

    return search_from_garbage_view(columns, where, db)


def search_from_garbage_view(columns, where: str, db: DB):
    if len(where) > 0:
        where = f"WHERE {where} "

    column = ", ".join(columns)
    cur = db.search(f"SELECT {column} FROM garbage {where};")
    if cur is None:
        return None
    res = cur.fetchall()
    return res


def count_garbage_by_time(uid: uid_t, db: DB):
    ti: time_t = time.time()
    start = ti - 3.5 * 24 * 60 * 60  # 前后3.5天
    end = ti + 3.5 * 24 * 60 * 60
    cur = db.search(f"SELECT GarbageID "
                    f"FROM garbage_time "
                    f"WHERE UserID = '{uid}' AND UseTime BETWEEN {mysql_time(start)} AND {mysql_time(end)};")
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
    return __find_garbage(f"SELECT GarbageID FROM garbage_n WHERE GarbageID = {gid};", 1, db)[0]


def find_wait_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[int, bytes, str, str, str]
    gb: GarbageBag
    gb, res = __find_garbage(f"SELECT GarbageID, GarbageType, UseTime, UserID, Location "
                             f"FROM garbage_c "
                             f"WHERE GarbageID = {gid};", 5, db)
    if gb is None:
        return None

    garbage_type: enum = int(res[1].decode())
    use_time: time_t = time_from_mysql(res[2])
    uid: uid_t = res[3]
    loc: location_t = res[4]

    gb.config_use(garbage_type, use_time, uid, loc)
    return gb


def find_use_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[int, bytes, str, str, str, bytes]
    gb: GarbageBag
    gb, res = __find_garbage(f"SELECT GarbageID, GarbageType, UseTime, UserID, Location, CheckResult, CheckerID "
                             f"FROM garbage_u "
                             f"WHERE GarbageID = {gid};", 7, db)
    if gb is None:
        return None

    garbage_type: enum = int(res[1].decode())
    use_time: time_t = time_from_mysql(res[2])
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
    cur = db.search(f"SELECT GarbageID, Flat FROM garbage WHERE GarbageID = {gid};")
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
        if garbage.is_check()[0]:
            db.done_(f"UPDATE garbage SET "
                     f"Flat = 2,"
                     f"UserID = '{info['user']}',"
                     f"UseTime = {time_from_mysql(info['use_time'])},"
                     f"GarbageType = {info['type']},"
                     f"Location = '{info['loc']}',"
                     f"CheckResult = {info['check']},"
                     f"CheckerID = '{info['checker']}',"
                     f"WHERE GarbageID = {gid};")
        elif garbage.is_use():
            db.done_(f"UPDATE garbage SET "
                     f"Flat = 1,"
                     f"UserID = '{info['user']}',"
                     f"UseTime = {time_from_mysql(info['use_time'])},"
                     f"GarbageType = {info['type']},"
                     f"Location = '{info['loc']}',"
                     f"CheckResult = NULL,"
                     f"CheckerID = NULL,"
                     f"WHERE GarbageID = {gid};")
        else:
            db.done_(f"UPDATE garbage SET "
                     f"Flat = 0,"
                     f"UserID = NULL,"
                     f"UseTime = NULL,"
                     f"GarbageType = NULL,"
                     f"Location = NULL,"
                     f"CheckResult = NULL,"
                     f"CheckerID = NULL,"
                     f"WHERE GarbageID = {gid};")
    except DBDoneException:
        return False
    finally:
        db.done_commit()
    return True


def create_new_garbage(db: DB) -> Optional[GarbageBag]:
    cur = db.done(f"INSERT INTO garbage(CreateTime, Flat) VALUES ({mysql_time()}, 0);")
    if cur is None:
        return None
    assert cur.rowcount == 1
    gid = cur.lastrowid
    return GarbageBag(str(gid))


def del_garbage_not_use(gid: gid_t, db: DB) -> bool:
    cur = db.done(f"DELETE FROM garbage_n WHERE GarbageID = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_wait_check(gid: gid_t, db: DB) -> bool:
    cur = db.done(f"DELETE FROM garbage_c WHERE GarbageID = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_has_check(gid: gid_t, db: DB) -> bool:
    cur = db.done(f"DELETE FROM garbage_u WHERE GarbageID = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage(gid, db: DB):
    cur = db.done(f"DELETE FROM garbage WHERE GarbageID = {gid};")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_where_not_use(where, db: DB) -> int:
    cur = db.done_(f"DELETE FROM garbage_n WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_wait_check(where, db: DB) -> int:
    cur = db.done_(f"DELETE FROM garbage_c WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_has_check(where, db: DB) -> int:
    cur = db.done_(f"DELETE FROM garbage_u WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_not_use(where, db: DB) -> int:
    cur = db.done(f"SELECT GarbageID FROM garbage_n WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_wait_check(where, db: DB) -> int:
    cur = db.done(f"SELECT GarbageID FROM garbage_c WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_has_check(where, db: DB) -> int:
    cur = db.done(f"SELECT GarbageID FROM garbage_u WHERE {where};")
    if cur is None:
        return -1
    return cur.rowcount


def del_all_garbage(db: DB) -> int:
    cur = db.done(f"DELETE FROM garbage WHERE 1;")
    if cur is None:
        return -1
    return cur.rowcount


def del_all_garbage_scan(db: DB) -> int:
    cur = db.done(f"SELECT GarbageID FROM garbage WHERE 1;")
    if cur is None:
        return -1
    return cur.rowcount


if __name__ == '__main__':
    mysql_db = DB()
    bag = create_new_garbage(mysql_db)
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
