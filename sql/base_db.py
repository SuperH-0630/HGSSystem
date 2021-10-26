import abc


class DBException(Exception):
    ...


class DBDoneException(DBException):
    ...


class DBCloseException(DBException):
    ...


class DBBit:
    BIT_0 = b'\x00'
    BIT_1 = b'\x01'


class Database(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, host: str, name: str, passwd: str):
        self._host = host
        self._name = name
        self._passwd = passwd

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
