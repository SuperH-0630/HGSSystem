from .font.noto import noto_font


class ConfigMatplotlibRelease:
    """ Matplotlib 相关配置 """
    matplotlib_font_dict = dict(fname=noto_font)


ConfigMatplotlib = ConfigMatplotlibRelease
