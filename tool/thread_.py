import threading
import traceback


class Threading(threading.Thread):
    """
    子线程
    """

    def __init__(self, func, *args, start_now: bool = True):
        """
        :param func: 子线程函数
        :param args: 子线程参数
        :param start_now: 是否马上运行 (否则要回调.start函数)
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.result = None

        if start_now:
            self.start()

    def run(self):
        try:
            self.result = self.func(*self.args)
        except:
            traceback.print_exc()
        finally:
            del self.func, self.args

    def wait_event(self) -> any:
        """
        等待线程结束
        :return: 线程函数的返回值
        """
        self.join()
        return self.result
