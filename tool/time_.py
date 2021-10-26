from .type_ import *
import time


class HGSTime:
    def __init__(self, second: time_t = None):
        if second is None:
            self._time: time_t = time_t(time.time())
        else:
            self._time: time_t = time_t(second)
        self._time_local: time.struct_time = time.localtime(self._time)

    def get_time(self) -> time_t:
        return self._time

    def is_out_of_date(self):
        return time.time() > self._time


def mysql_time(t=None) -> str:
    if t is None:
        t = time.time()
    return f'from_unixtime({t})'


def time_from_mysql(t) -> float:
    t_struct = time.strptime(str(t), '%Y-%m-%d %H:%M:%S')
    return time.mktime(t_struct)


hgs_time_t = Union[HGSTime, time_t]
