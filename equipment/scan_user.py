import re
import os.path
from PIL import Image, ImageDraw, ImageFont

from conf import Config
from core.user import User
from sql import DBBit
from sql.db import DB
from sql.user import find_user_by_id
from tool.typing import *
from .scan import QRCode

qr_user_pattern = re.compile(r'HGSSystem-QR-USER:([a-z0-9]{32})-END', re.I)
qr_img_title_font = ImageFont.truetype(font=Config.font_d["noto-bold"], size=35, encoding="unic")
qr_img_title_b_font = ImageFont.truetype(font=Config.font_d["noto-medium"], size=30, encoding="unic")
qr_img_info_font = ImageFont.truetype(font=Config.font_d["noto"], size=30, encoding="unic")


def scan_uid(code: QRCode) -> uid_t:
    data = code.get_data()
    res = re.match(qr_user_pattern, data)
    print(data, res)
    if res is None:
        return ""
    else:
        return res.group(1)


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


def make_uid_image(uid: uid_t, name: uname_t, is_manager: bool, path: str):
    qr = QRCode(f"HGSSystem-QR-USER:{uid}-END")
    qr_img = qr.make_img().convert("RGB").resize((500, 500))
    if qr_img is None:
        return False

    title = f"HGSSystem 用户ID"
    title_width, title_height = qr_img_title_font.getsize(title)
    name_width, name_height = qr_img_title_b_font.getsize(name)
    uid_width, uid_height = qr_img_info_font.getsize(uid[:Config.show_uid_len])
    uid_color = (220, 20, 60) if is_manager else (0, 0, 0)

    if name_width > 510:
        name_width = 510

    image = Image.new('RGB', (510, 500 + title_height + name_height + 110), (255, 255, 255))
    logo_image = Image.open(Config.picture_d['logo']).resize((64, 64))

    draw = ImageDraw.Draw(image)
    draw.text((((510 - title_width) / 2), 5), title, (0, 0, 0), font=qr_img_title_font)
    draw.text((((510 - name_width) / 2), title_height + 5), name, (0, 0, 0), font=qr_img_title_b_font)

    qr_img.paste(logo_image, (int((500 - 64) / 2), int((500 - 64) / 2)))
    image.paste(qr_img, (5, title_height + name_height + 10))
    draw.text((((510 - uid_width) / 2), 500 + title_height + name_height + 10), uid[:Config.show_uid_len],
              uid_color, font=qr_img_info_font)

    image.save(path)
    return True


def write_uid_qr(uid: uid_t, path: str, db: DB, name="nu") -> Tuple[str, Optional[User]]:
    user = find_user_by_id(uid, db)
    if user is None:
        return "", None

    user_name = user.get_name()
    is_manager = user.is_manager()
    path = __get_uid_qr_file_name(uid, user_name, path, name)
    if make_uid_image(uid, user_name, is_manager, path):
        return path, user
    return "", None


def write_all_uid_qr(path: str, db: DB, name="nu", where: str = "") -> List[str]:
    cur = db.search(columns=["UserID", "Name", "IsManager"], table="user", where=where)
    if cur is None:
        return []

    re_list = []
    for _ in range(cur.rowcount):
        res = cur.fetchone()
        assert len(res) == 3
        path_ = __get_uid_qr_file_name(res[0], res[1], path, name)
        if make_uid_image(res[0], res[1], res[2] == DBBit.BIT_1, path_):
            re_list.append(path_)
    return re_list
