import pymysql
import threading
import traceback

from conf import mysql_url, mysql_name, mysql_passwd
from .base_db import Database, DBCloseException
from tool.type_ import *


class MysqlDB(Database):
    def __init__(self, host: str = mysql_url, name: str = mysql_name, passwd: str = mysql_passwd):
        super(MysqlDB, self).__init__(host, name, passwd)
        try:
            self._db = pymysql.connect(user=self._name, password=self._passwd, host=self._host, database="hgssystem")
        except pymysql.err.OperationalError:
            raise
        self._cursor = self._db.cursor()
        self._lock = threading.RLock()

    def close(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._db is not None:
            self._db.close()
        self._db = None
        self._cursor = None
        self._lock = None

    def is_connect(self) -> bool:
        if self._cursor is None or self._db is None:
            return False
        return True

    def get_cursor(self) -> pymysql.cursors.Cursor:
        if self._cursor is None or self._db is None:
            raise DBCloseException
        return self._cursor

    def search(self, sql) -> Union[None, pymysql.cursors.Cursor]:
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
        return self._cursor

    def done(self, sql) -> Union[None, pymysql.cursors.Cursor]:
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
        return self._cursor

    def done_(self, sql) -> Union[None, pymysql.cursors.Cursor]:
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
            self._lock.release()
        return self._cursor

    def done_commit(self):
        try:
            self._lock.acquire()
            self._db.commit()
        except pymysql.err:
            traceback.print_exc()
        finally:
            self._lock.release()
