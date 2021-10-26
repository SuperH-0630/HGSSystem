import conf
from .base_db import DBBit, DBException, DBCloseException, DBDataException, DBDoneException  # 导入必要的内容

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


def search_from_garbage_checker_user(columns, where, db: DB):
    if len(where) > 0:
        where = f"WHERE {where} "

    column = ", ".join(columns)
    cur = db.search(f"SELECT {column} FROM garbage_checker_user {where};")
    if cur is None:
        return None
    res = cur.fetchall()
    return res
