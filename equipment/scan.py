import time
import threading
import cv2.cv2 as cv2
from PIL.Image import Image, FLIP_LEFT_RIGHT, fromarray
import io
import numpy as np

from conf import Config
import qrcode
from tool.typing import *

if Config.use_opencv:
    class HGSCapture:
        """ 摄像头扫描 """

        def __init__(self, capnum: int = Config.capture_num, *args, **kwargs):
            args = *args, *Config.capture_arg
            if cv2.CAP_DSHOW not in args:
                args = *args, cv2.CAP_DSHOW
            self._capture = cv2.VideoCapture(int(capnum), *args, **kwargs)
            self._frame = None
            self._lock = threading.RLock()

        def get_image(self) -> bool:
            """ 获取摄像头图像 """
            try:
                self._lock.acquire()
                ret, frame = self._capture.read()
                if ret:
                    self._frame = frame
            finally:
                self._lock.release()
            return ret

        def get_frame(self) -> Image:
            """ 获取 frame """
            try:
                self._lock.acquire()
                frame = fromarray(cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)).transpose(FLIP_LEFT_RIGHT)
            finally:
                self._lock.release()
            return frame
else:
    import picamera


    class HGSCapture:
        """ 摄像头扫描 """

        def __init__(self):
            self._frame = None
            self._lock = threading.RLock()

        def get_image(self) -> bool:
            """ 获取摄像头图像 """
            try:
                self._lock.acquire()
                stream = io.BytesIO()
                with picamera.PiCamera() as camera:
                    camera.start_preview()
                    time.sleep(2)
                    camera.capture(stream, format='jpeg')
                # 将指针指向流的开始
                stream.seek(0)
                self._frame = Image.open(stream)
            except:
                return False
            finally:
                self._lock.release()
            return True

        def get_frame(self) -> Image:
            """ 获取 frame """
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

    def save_img(self, image: str) -> bool:
        try:
            with open(image, "wb") as f:
                img = self.make_img()
                img.save(f)
        except (IOError, FileExistsError, FileNotFoundError):
            return False
        else:
            return True

    def make_img(self) -> Image:
        qr = qrcode.QRCode(
            version=None,
            box_size=10,
            border=4
        )
        qr.add_data(self._data)
        qr.make(fit=True)
        return qr.make_image()


class HGSQRCoder:
    """ 二维码扫描仪 """

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

            frame: Image = self._cap.get_frame().transpose(FLIP_LEFT_RIGHT)
            gray = cv2.cvtColor(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
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
