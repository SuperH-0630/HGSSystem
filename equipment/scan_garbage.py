import re
import os.path
from PIL import Image, ImageDraw, ImageFont

from conf import Config
from core.garbage import GarbageBag
from sql.db import DB
from sql.garbage import find_garbage
from tool.typing import *
from .scan import QRCode

qr_user_pattern = re.compile(r'HGSSystem-QR-GARBAGE:([a-z0-9]+)-END', re.I)
qr_img_title_font = ImageFont.truetype(font=Config.font_d["noto-bold"], size=35, encoding="unic")
qr_img_title_b_font = ImageFont.truetype(font=Config.font_d["noto-medium"], size=30, encoding="unic")
qr_img_info_font = ImageFont.truetype(font=Config.font_d["noto"], size=30, encoding="unic")
qr_Watermark = ImageFont.truetype(font=Config.font_d["noto-black"], size=55, encoding="unic")


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
    qr_img = qr.make_img().convert("RGB").resize((500, 500))
    if not qr_img:
        return False

    title = f"HGSSystem 垃圾袋ID"
    loc = f"垃圾站: {Config.base_location}"
    title_width, title_height = qr_img_title_font.getsize(title)
    loc_width, loc_height = qr_img_title_b_font.getsize(loc)
    if len(str(gid)) > Config.show_gid_len:
        gid = gid[-Config.show_gid_len:]
    gid_width, gid_height = qr_img_info_font.getsize(gid)

    if loc_width > 510:
        loc_width = 510

    image = Image.new('RGB', (510, 500 + title_height + loc_height + 110), (255, 255, 255))
    logo_image = Image.open(Config.picture_d['logo']).resize((64, 64))

    draw = ImageDraw.Draw(image)
    draw.text((((510 - title_width) / 2), 5), title, (0, 0, 0), font=qr_img_title_font)
    draw.text((((510 - loc_width) / 2), title_height + 5), loc, (0, 0, 0), font=qr_img_title_b_font)

    qr_img.paste(logo_image, (int((500 - 64) / 2), int((500 - 64) / 2)))
    image.paste(qr_img, (5, title_height + loc_height + 10))

    draw.text((((510 - gid_width) / 2), 500 + title_height + loc_height + 10), gid, (0, 0, 0), font=qr_img_info_font)

    image.save(path)
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
        if make_gid_image(str(res[0]), path_):
            re_list.append((path_,))
    return re_list
