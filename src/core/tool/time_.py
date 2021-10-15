from .type_ import *
import time


class HGSTime:
    def __init__(self, second: time_t = None):
        if second is None:
            self._time: time_t = time.time()
        else:
            self._time: time_t = second
        self._time_local: time.struct_time = time.localtime(self._time)

    def is_out_of_date(self):
        return time.time() > self._time


hgs_time_t: TypeAlias = Union[HGSTime, time_t]
