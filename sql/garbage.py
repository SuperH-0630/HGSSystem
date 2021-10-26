import time
from . import DBBit
from .db import DB
from tool.type_ import *
from tool.time_ import mysql_time, time_from_mysql
from core.garbage import GarbageBag, GarbageType


def update_garbage_type(where: str, type_: int, db: DB) -> int:
    if len(where) == 0:
        return -1

    cur = db.update(table="garbage", kw={"GarbageType": str(type_)}, where=where)
    if cur is None:
        return -1
    return cur.rowcount


def update_garbage_check(where: str, check_: bool, db: DB) -> int:
    if len(where) == 0:
        return -1

    i: str = '1' if check_ else '0'
    cur = db.update(table="garbage", kw={"CheckResult": i}, where=where)
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
    cur = db.search(columns=columns, table="garbage", where=where)
    if cur is None:
        return None
    res = cur.fetchall()
    return res


def count_garbage_by_time(uid: uid_t, db: DB):
    ti: time_t = time.time()
    start = ti - 3.5 * 24 * 60 * 60  # 前后3.5天
    end = ti + 3.5 * 24 * 60 * 60
    cur = db.search(columns=["GarbageID"],
                    table="garbage_time",
                    where=[f"UserID = '{uid}'", f"UseTime BETWEEN {mysql_time(start)} AND {mysql_time(end)}"])
    if cur is None:
        return -1
    return cur.rowcount


def __find_garbage(columns: List[str], table: str, where: str, db: DB):
    cur = db.search(columns=columns, table=table, where=where)
    if cur is None or cur.rowcount == 0:
        return [None, tuple()]
    assert cur.rowcount == 1
    res = cur.fetchone()
    assert len(res) == len(columns)
    return GarbageBag(str(res[0])), res


def find_not_use_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    return __find_garbage(columns=["GarbageID"],
                          table="garbage_n",
                          where=f"GarbageID = {gid}",
                          db=db)[0]


def find_wait_garbage(gid: gid_t, db: DB) -> Union[GarbageBag, None]:
    res: Tuple[int, bytes, str, str, str]
    gb: GarbageBag
    gb, res = __find_garbage(columns=["GarbageID", "GarbageType", "UseTime", "UserID", "Location"],
                             table="garbage_c",
                             where=f"GarbageID = {gid}",
                             db=db)[0]
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
    gb, res = __find_garbage(columns=["GarbageID", "GarbageType", "UseTime", "UserID", "Location",
                                      "CheckResult", "CheckerID"],
                             table="garbage_u",
                             where=f"GarbageID = {gid}",
                             db=db)[0]
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
    cur = db.search(columns=["GarbageID", "Flat"],
                    table="garbage",
                    where=f"GarbageID = {gid}")
    if cur is None or cur.rowcount == 0:
        return False, 0
    assert cur.rowcount == 1
    res: Tuple[int, int] = cur.fetchone()
    return True, res[1]


def update_garbage(garbage: GarbageBag, db: DB) -> bool:
    re = find_garbage(garbage.get_gid(), db)
    if re is None:
        return False

    if re.is_use() and not garbage.is_use() or re.is_check()[0] and not garbage.is_check()[0]:
        return False

    if not garbage.is_use() and not garbage.is_check()[0]:
        return True  # 不做任何修改

    gid = garbage.get_gid()
    info = garbage.get_info()

    update_kw = {
        "Flat": "0",
        "UserID": "NULL",
        "UseTime": "NULL",
        "GarbageType": "NULL",
        "Location": "NULL",
        "CheckResult": "NULL",
        "CheckerID": "NULL"
    }

    if garbage.is_use():
        update_kw['Flat'] = "1"
        update_kw['UserID'] = f"'{info['user']}'"
        update_kw['UseTime'] = f"{mysql_time(info['use_time'])}"
        update_kw['GarbageType'] = f"{info['type']}"
        update_kw['Location'] = f"'{info['loc']}'"

    if garbage.is_check()[0]:
        update_kw['Flat'] = "2"
        update_kw['CheckResult'] = f"{info['check']}"
        update_kw['CheckerID'] = f"'{info['checker']}'"

    res = db.update("garbage", kw=update_kw, where=f"GarbageID = {gid}")
    return res is not None


def create_new_garbage(db: DB) -> Optional[GarbageBag]:
    cur = db.insert(table="garbage", columns=["CreateTime", "Flat"], values=f"{mysql_time()}, 0")
    print(cur)
    if cur is None:
        return None
    assert cur.rowcount == 1
    gid = cur.lastrowid
    return GarbageBag(str(gid))


def del_garbage_not_use(gid: gid_t, db: DB) -> bool:
    cur = db.delete(table="garbage_n", where=f"GarbageID = {gid}")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_wait_check(gid: gid_t, db: DB) -> bool:
    cur = db.delete(table="garbage_c", where=f"GarbageID = {gid}")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_has_check(gid: gid_t, db: DB) -> bool:
    cur = db.delete(table="garbage_u", where=f"GarbageID = {gid}")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage(gid, db: DB):
    cur = db.delete(table="garbage", where=f"GarbageID = {gid}")
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    return True


def del_garbage_where_not_use(where: str, db: DB) -> int:
    cur = db.delete(table="garbage_n", where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_wait_check(where: str, db: DB) -> int:
    cur = db.delete(table="garbage_c", where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_has_check(where: str, db: DB) -> int:
    cur = db.delete(table="garbage_u", where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_not_use(where, db: DB) -> int:
    cur = db.search(columns=["GarbageID"],
                    table="garbage_n",
                    where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_wait_check(where: str, db: DB) -> int:
    cur = db.search(columns=["GarbageID"],
                    table="garbage_c",
                    where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_garbage_where_scan_has_check(where, db: DB) -> int:
    cur = db.search(columns=["GarbageID"],
                    table="garbage_u",
                    where=where)
    if cur is None:
        return -1
    return cur.rowcount


def del_all_garbage(db: DB) -> int:
    cur = db.delete(table="garbage", where='1')
    if cur is None:
        return -1
    return cur.rowcount


def del_all_garbage_scan(db: DB) -> int:
    cur = db.search(columns=["GarbageID"], table="garbage", where="1")
    if cur is None:
        return -1
    return cur.rowcount
