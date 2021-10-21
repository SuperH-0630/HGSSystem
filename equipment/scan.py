import time
import threading
import cv2 as cv2

import conf
import qrcode
from tool.type_ import *


class HGSCapture:
    def __init__(self, capnum: int = conf.capture_num, *args, **kwargs):
        args = *args, *conf.capture_arg
        if cv2.CAP_DSHOW not in args:
            args = *args, cv2.CAP_DSHOW
        self._capture = cv2.VideoCapture(capnum, *args, **kwargs)
        self._frame = None
        self._lock = threading.RLock()

    def get_image(self):
        try:
            self._lock.acquire()
            ret, frame = self._capture.read()
            if ret:
                self._frame = frame
        finally:
            self._lock.release()
        return ret

    def get_frame(self):
        try:
            self._lock.acquire()
            frame = self._frame
        finally:
            self._lock.release()
        return frame


class QRCode:
    def __init__(self, data, get_time: Optional[time_t] = None):
        self._data: str = data
        if get_time is None:
            get_time = time.time()
        self._time: time_t = get_time

    def __repr__(self):
        return f"QR:'{self._data}'"

    def get_data(self):
        return self._data

    def get_time(self):
        return self._time

    def make_img(self, image: str) -> bool:
        try:
            with open(image, "wb") as f:
                img = qrcode.make(self._data)
                img.save(f)
        except (IOError, FileExistsError, FileNotFoundError):
            return False
        else:
            return True


class HGSQRCoder:
    def __init__(self, cap: HGSCapture):
        self._cap = cap
        self._last_qr: Optional[QRCode] = None
        self._lock = threading.RLock()

    def get_qr_code(self) -> Optional[QRCode]:
        try:
            self._lock.acquire()
            re = self.is_qr_code()
            last_qr = self._last_qr
        finally:
            self._lock.release()

        if re:
            return last_qr
        return None

    def is_qr_code(self) -> bool:
        try:
            self._lock.acquire()

            frame = self._cap.get_frame()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            coder = cv2.QRCodeDetector()

            try:
                data, points, straight_qrcode = coder.detectAndDecode(gray)
            except cv2.error:
                return False

            old_qr: Optional[QRCode] = self._last_qr

            if len(data) > 0:
                self._last_qr = QRCode(data)
                return old_qr is None or data != old_qr.get_data()
            elif len(data) == 0 and old_qr is not None:
                if time.time() - old_qr.get_time() >= 1.5:  # 时间间隔大于2s 自动取消
                    self._last_qr = QRCode(data)
            return False

        finally:
            self._lock.release()
