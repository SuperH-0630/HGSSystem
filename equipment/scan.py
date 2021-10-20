import time
import conf
import cv2 as cv2
import qrcode
from tool.type_ import *


class HGSCapture:
    def __init__(self, capnum: int = conf.capture_num, *args, **kwargs):
        args = *args, *conf.capture_arg
        if cv2.CAP_DSHOW not in args:
            args = *args, cv2.CAP_DSHOW
        self._capture = cv2.VideoCapture(capnum, *args, **kwargs)
        self._frame = None

    def get_image(self):
        ret, frame = self._capture.read()
        if ret:
            self._frame = frame
        return ret

    def show_image_wait_second(self, wait_second: int = 10):
        cv2.imshow('frame', self._frame)
        if wait_second != 0:
            return cv2.waitKey(wait_second * 1000)
        return None

    def show_image(self, wait: int = 10):
        cv2.imshow('frame', self._frame)
        if wait != 0:
            return cv2.waitKey(wait)
        return None

    def get_frame(self):
        return self._frame


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

    def get_qr_code(self) -> Optional[QRCode]:
        re = self.is_qr_code()
        if re:
            return self._last_qr
        return None

    def is_qr_code(self) -> bool:
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


if __name__ == '__main__':
    capture = HGSCapture()
    qr_capture = HGSQRCoder(capture)
    while True:
        capture.get_image()
        qr_data = qr_capture.get_qr_code()
        if qr_data is not None:
            print(qr_data)
            qr_data.make_img("img.png")
        capture.show_image(0)
        if cv2.waitKey(1) == ord('q'):
            break
