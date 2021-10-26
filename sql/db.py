import conf
from tool.type_ import List

if conf.database.upper() == 'MYSQL':
    try:
        from .mysql_db import MysqlDB
    except ImportError:
        print("Can not import mysqlDB")
        raise
    else:
        DB = MysqlDB
else:
    print(f"Not support database: {conf.database}")
    raise Exception


def search_from_garbage_checker_user(columns: List[str], where, db: DB):
    cur = db.search(columns=columns, table='garbage_checker_user', where=where)
    if cur is None:
        return None
    res = cur.fetchall()
    return res
