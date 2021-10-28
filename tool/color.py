import random
from PIL import Image


# RGB格式颜色转换为16进制颜色格式
def rgb_to_hex(rgb: tuple):
    color = '#'
    for i in rgb:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    return color


def random_color(n=100, m=255):
    return rgb_to_hex((random.randint(n, m), random.randint(n, m), random.randint(n, m)))
