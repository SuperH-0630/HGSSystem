import abc
import traceback
import threading

import conf
from tool.type_ import *


class TkEventException(Exception):
    ...


class TkEventBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.thread: Optional[TkThreading] = None

    @abc.abstractmethod
    def is_end(self) -> bool:
        ...

    @abc.abstractmethod
    def get_title(self) -> str:
        ...

    @abc.abstractmethod
    def done_after_event(self):
        ...


class TkEventMain(metaclass=abc.ABCMeta):
    def __init__(self):
        self._event_list: List[TkEventBase] = []
        self.set_after_run(conf.tk_refresh_delay, lambda: self.run_event())

    def push_event(self, event: TkEventBase):
        self._event_list.append(event)
        self.show_loading(event.get_title())
        self.run_event()

    def run_event(self):
        if len(self._event_list) == 0:
            return

        new_event: List[TkEventBase] = []
        done_event: List[TkEventBase] = []
        for event in self._event_list:
            if event.is_end():
                done_event.append(event)
            else:
                new_event.append(event)
        self._event_list = new_event
        if len(self._event_list) == 0:
            self.stop_loading()

        for event in done_event:  # 隐藏进度条后执行Event-GUI任务
            try:
                event.done_after_event()
            except:
                traceback.print_exc()
        self.set_after_run_now(conf.tk_refresh_delay, self.run_event)

    @abc.abstractmethod
    def show_loading(self, title: str):
        ...

    @abc.abstractmethod
    def stop_loading(self):
        ...

    @abc.abstractmethod
    def set_after_run(self, ms, func, *args):
        ...

    @abc.abstractmethod
    def set_after_run_now(self, ms, func, *args):
        ...


class TkThreading(threading.Thread):
    def __init__(self, func, *args, start_now: bool = True):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.result = None

        if start_now:
            self.start()

    def run(self):
        self.result = self.func(*self.args)

    def wait_event(self):
        self.join()
        return self.result
