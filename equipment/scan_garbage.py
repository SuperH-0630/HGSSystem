from core.garbage import GarbageBag
from sql.db import DB
from sql.garbage import find_garbage
from tool.typing import *
from .scan import QRCode, HGSCapture, HGSQRCoder
from tool.pic import write_text
import re
import os.path

qr_user_pattern = re.compile(r'HGSSystem-QR-GARBAGE:([a-z0-9]+)-END', re.I)


def scan_gid(code: QRCode) -> gid_t:
    data = code.get_data()
    res = re.match(qr_user_pattern, data)
    if res is None:
        return ""
    else:
        return res.group(1)


def scan_garbage(code: QRCode, db: DB) -> Optional[GarbageBag]:
    gid = scan_gid(code)
    if len(gid) == 0:
        return None
    return find_garbage(gid, db)


def __get_gid_qr_file_name(gid: gid_t, path: str):
    path = os.path.join(path, f"gar-{gid}.png")
    dir_ = os.path.split(path)[0]
    if len(dir_) > 0:
        os.makedirs(dir_, exist_ok=True)  # 生成输出目录
    return path


def make_gid_image(gid: gid_t, path: str):
    qr = QRCode(f"HGSSystem-QR-GARBAGE:{gid}-END")
    res = qr.make_img(path)
    if not res:
        return False
    write_text((30, 5), "noto", f"GID: {gid}", path)
    return True


def write_gid_qr(gid: gid_t, path: str, db: DB) -> Tuple[str, Optional[GarbageBag]]:
    garbage = find_garbage(gid, db)
    if garbage is None:
        return "", None

    path = __get_gid_qr_file_name(gid, path)
    if make_gid_image(gid, path):
        return path, garbage
    return "", None


def write_all_gid_qr(path: str, db: DB, where: str = "") -> List[Tuple[str]]:
    cur = db.search(columns=["GarbageID"], table="garbage", where=where)
    if cur is None:
        return []

    re_list = []
    for _ in range(cur.rowcount):
        res = cur.fetchone()
        assert len(res) == 1
        path_ = __get_gid_qr_file_name(res[0], path)
        if make_gid_image(res[0], path_):
            re_list.append((path_,))
    return re_list
