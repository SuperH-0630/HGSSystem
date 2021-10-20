import conf
from core.user import User
from sql.db import DB, mysql_db
from sql.user import find_user_by_id
from type_ import *
from scan import QRCode, capture, qr_capture
from tool.pic import write_text
import re
import os.path


qr_user_pattern = re.compile(r'HGSSystem-QR-USER:([a-z0-9]{32})-END', re.I)


def scan_uid(code: QRCode) -> uid_t:
    data = code.get_data()
    res = re.match(qr_user_pattern, data)
    if res is None:
        return ""
    else:
        return res.group(1)


def scan_user(code: QRCode, db: DB) -> Optional[User]:
    uid = scan_uid(code)
    if len(uid) == 0:
        return None
    return find_user_by_id(uid, db)


def __get_uid_qr_file_name(uid: uid_t, name: str, path: str, name_type="nu"):
    if name_type == "nu":
        path = os.path.join(path, f"{name}-f{uid}.png")
    elif name_type == "n":
        path = os.path.join(path, f"{name}.png")
    else:
        path = os.path.join(path, f"{uid}.png")

    dir_ = os.path.split(path)[0]
    if len(dir_) > 0:
        os.makedirs(dir_, exist_ok=True)  # 生成输出目录
    return path


def make_uid_image(uid: uid_t, name: uname_t, path: str):
    qr = QRCode(f"HGSSystem-QR-USER:{uid}-END")
    res = qr.make_img(path)
    if not res:
        return False
    write_text((60, 5), "noto", f"User: {name} {uid[0: conf.qr_show_uid_len]}", path)
    return True


def write_uid_qr(uid: uid_t, path: str, db: DB, name="nu") -> Tuple[str, Optional[User]]:
    user = find_user_by_id(uid, db)
    if user is None:
        return "", None

    user_name = user.get_name()
    path = __get_uid_qr_file_name(uid, user_name, path, name)
    if make_uid_image(uid, user_name, path):
        return path, user
    return "", None


def write_all_uid_qr(path: str, db: DB, name="nu", where: str = "") -> List[str]:
    if len(where) > 0:
        where = f"WHERE {where}"

    cur = db.search(f"SELECT uid, name FROM user {where};")
    if cur is None:
        return []

    re_list = []
    for _ in range(cur.rowcount):
        res = cur.fetchone()
        assert len(res) == 2
        path_ = __get_uid_qr_file_name(res[0], res[1], path, name)
        if make_uid_image(res[0], res[1], path_):
            re_list.append(path_)
    return re_list


if __name__ == '__main__':
    write_all_uid_qr("uid", mysql_db)
    while True:
        capture.get_image()
        qr_data = qr_capture.get_qr_code()
        if qr_data is not None:
            usr = scan_user(qr_data, mysql_db)
            if usr is not None:
                print(usr)
        if capture.show_image(1) == ord('q'):
            break

