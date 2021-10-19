import conf
from .type_ import *
from PIL import Image, ImageDraw, ImageFont


def write_text(pos: Tuple[int, int], font: str, text: str, path: str):
    image = Image.open(path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font=conf.font_d[font], size=20)
    draw.text(pos, text, font=font)
    image.save(path)