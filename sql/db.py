import pymysql
from conf import MYSQL_URL, MYSQL_NAME, MYSQL_PASSWORD
from tool.type_ import *


class DBException(Exception):
    ...


class DBDataException(Exception):
    ...


class DBCloseException(Exception):
    ...


class DBDoneException(Exception):
    ...


class DBBit:
    BIT_0 = b'\x00'
    BIT_1 = b'\x01'


class DB:
    def __init__(self, host: str = MYSQL_URL, name: str = MYSQL_NAME, passwd: str = MYSQL_PASSWORD):
        try:
            self._db = pymysql.connect(user=name, password=passwd, host=host, database="hgssystem")
        except pymysql.err.OperationalError:
            raise DBException
        self._cursor = self._db.cursor()

    def __del__(self):
        self.close()

    def close(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._db is not None:
            self._db.close()
        self._db = None
        self._cursor = None

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
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            return None
        return self._cursor

    def done(self, sql) -> Union[None, pymysql.cursors.Cursor]:
        if self._cursor is None or self._db is None:
            raise DBCloseException

        try:
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            self._db.rollback()
            return None
        finally:
            self._db.commit()
        return self._cursor

    def done_(self, sql) -> Union[None, pymysql.cursors.Cursor]:
        if self._cursor is None or self._db is None:
            raise DBCloseException
        try:
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            self._db.rollback()
            raise DBDoneException
        return self._cursor

    def done_commit(self):
        self._db.commit()


mysql_db = DB()

if __name__ == '__main__':
    # 测试程序
    mysql_db = DB()
    mysql_db.search("SELECT * FROM user;")
    res = mysql_db.get_cursor().fetchall()
    print(res)

    mysql_db.search("SELECT * FROM user WHERE uid = 0;")
    res = mysql_db.get_cursor().fetchall()
    print(res)
    mysql_db.close()
