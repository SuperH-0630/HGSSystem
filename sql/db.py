import abc
import pymysql
import threading
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


class Database(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, host: str, name: str, passwd: str):
        pass

    @abc.abstractmethod
    def close(self):
        """
        关闭数据库, 此代码执行后任何成员函数再被调用其行为是未定义的
        :return:
        """
        ...

    @abc.abstractmethod
    def is_connect(self) -> bool:
        """
        :return: 是否处于连接状态
        """
        ...

    @abc.abstractmethod
    def get_cursor(self) -> any:
        """
        :return: 返回数据库游标
        """
        ...

    @abc.abstractmethod
    def search(self, sql) -> any:
        """
        执行SQL语句, 仅SELECT
        :param sql: SELECT的SQL语句
        :return: 游标
        """
        ...

    @abc.abstractmethod
    def done(self, sql) -> any:
        """
        执行SQL语句, 并提交
        :param sql: SQL语句
        :return: 游标
        """
        ...

    @abc.abstractmethod
    def done_(self, sql) -> any:
        """
        执行SQL语句, 但暂时不提交
        :param sql: SQL语句
        :return: 游标
        """
        ...

    @abc.abstractmethod
    def done_commit(self):
        """
        提交由 done_ 执行的SQL语句
        :return:
        """
        ...


class MysqlDB(Database):
    def __init__(self, host: str = MYSQL_URL, name: str = MYSQL_NAME, passwd: str = MYSQL_PASSWORD):
        try:
            self._db = pymysql.connect(user=name, password=passwd, host=host, database="hgssystem")
        except pymysql.err.OperationalError:
            raise DBException
        self._cursor = self._db.cursor()
        self._lock = threading.RLock()

    def __del__(self):
        self.close()

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
        finally:
            self._lock.release()
        return self._cursor

    def done_commit(self):
        try:
            self._lock.acquire()
            self._db.commit()
        finally:
            self._lock.release()


DB = MysqlDB  # DB使用MySQL


def search_from_garbage_checker_user(columns, where, db: DB):
    if len(where) > 0:
        where = f"WHERE {where} "

    column = ", ".join(columns)
    cur = db.search(f"SELECT {column} FROM garbage_checker_user {where};")
    if cur is None:
        return None
    res = cur.fetchall()
    return res


if __name__ == '__main__':
    # 测试程序
    mysql_db = DB()
    mysql_db.search("SELECT * FROM user;")
    res_ = mysql_db.get_cursor().fetchall()
    print(res_)

    mysql_db.search("SELECT * FROM user WHERE uid = 0;")
    res_ = mysql_db.get_cursor().fetchall()
    print(res_)
    mysql_db.close()
