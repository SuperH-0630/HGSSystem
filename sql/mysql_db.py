import pymysql
import threading
import traceback

from conf import mysql_url, mysql_name, mysql_passwd
from .base_db import HGSDatabase, DBCloseException, HGSCursor
from tool.type_ import *


class MySQLCursor(HGSCursor):
    def __init__(self, cursor: pymysql.cursors.Cursor):
        self._cursor: pymysql.cursors.Cursor = cursor

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()


class MysqlDB(HGSDatabase):
    def __init__(self, host: str = mysql_url, name: str = mysql_name, passwd: str = mysql_passwd):
        super(MysqlDB, self).__init__(host, name, passwd)
        try:
            self._db = pymysql.connect(user=self._name, password=self._passwd, host=self._host, database="hgssystem")
        except pymysql.err.OperationalError:
            raise
        self._cursor: pymysql.cursors.Cursor = self._db.cursor()
        self._mysql_cursor = MySQLCursor(self._cursor)
        self._lock = threading.RLock()

    def close(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._db is not None:
            self._db.close()
        self._db = None
        self._cursor = None
        self._mysql_cursor = None
        self._lock = None

    def is_connect(self) -> bool:
        if self._cursor is None or self._db is None:
            return False
        return True

    def get_cursor(self) -> HGSCursor:
        if self._cursor is None or self._db is None:
            raise DBCloseException
        return self._mysql_cursor

    def search(self, columns: List[str], table: str,
               where: Union[str, List[str]] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None,
               order_by: Optional[List[Tuple[str, str]]] = None):
        if type(where) is list and len(where) > 0:
            where: str = " WHERE " + " AND ".join(f"({w})" for w in where)
        elif type(where) is str and len(where) > 0:
            where = " WHERE " + where
        else:
            where: str = ""

        if order_by is None:
            order_by: str = ""
        else:
            by = [f" {i[0]} {i[1]} " for i in order_by]
            order_by: str = " ORDER BY" + ", ".join(by)

        if limit is None:
            limit: str = ""
        else:
            limit = f" LIMIT {limit}"

        if offset is None:
            offset: str = ""
        else:
            offset = f" OFFSET {offset}"

        columns: str = ", ".join(columns)
        return self.__search(f"SELECT {columns} FROM {table} {where} {order_by} {limit} {offset};")

    def insert(self, table: str, columns: list, values: Union[str, List[str]]):
        columns: str = ", ".join(columns)
        if type(values) is str:
            values: str = f"({values})"
        else:
            values: str = ", ".join(f"{v}" for v in values)
        return self.__done(f"INSERT INTO {table}({columns}) VALUES {values};")

    def delete(self, table: str, where: Union[str, List[str]] = None):
        if type(where) is list and len(where) > 0:
            where: str = " AND ".join(f"({w})" for w in where)
        elif type(where) is not str or len(where) == 0:  # 必须指定条件
            return None

        return self.__done(f"DELETE FROM {table} WHERE {where};")

    def update(self, table: str, kw: dict[str:str], where: Union[str, List[str]] = None):
        if len(kw) == 0:
            return None

        if type(where) is list and len(where) > 0:
            where: str = " AND ".join(f"({w})" for w in where)
        elif type(where) is not str or len(where) == 0:  # 必须指定条件
            return None

        kw_list = [f"{key} = {kw[key]}" for key in kw]
        kw_str = ", ".join(kw_list)

        return self.__done(f"UPDATE {table} SET {kw_str} WHERE {where};")

    def __search(self, sql) -> Union[None, HGSCursor]:
        if self._cursor is None or self._db is None:
            raise DBCloseException

        try:
            self._lock.acquire()  # 上锁
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            print(f"{sql}")
            traceback.print_exc()
            return None
        finally:
            self._lock.release()  # 释放锁
        return self._mysql_cursor

    def __done(self, sql) -> Union[None, HGSCursor]:
        if self._cursor is None or self._db is None:
            raise DBCloseException

        try:
            self._lock.acquire()
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            self._db.rollback()
            print(f"{sql}")
            traceback.print_exc()
            return None
        finally:
            self._db.commit()
            self._lock.release()
        return self._mysql_cursor
