import abc


class TkEventBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_end(self) -> bool:
        ...

    @abc.abstractmethod
    def get_title(self) -> str:
        ...

    @abc.abstractmethod
    def done_after_event(self):
        ...
