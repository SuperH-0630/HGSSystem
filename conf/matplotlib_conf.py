class ConfigMatplotlibRelease:
    """ Matplotlib 相关配置 """
    matplotlib_font = "SimHei"
    matplotlib_font_dict = dict(family=matplotlib_font)


ConfigMatplotlib = ConfigMatplotlibRelease

try:
    import matplotlib.font_manager as fm
except ImportError:
    pass
else:
    if "SimHei" not in [f.name for f in fm.fontManager.ttflist]:
        print("请安装SimHei字体")
        exit(1)
    fm.rcParams["font.sans-serif"] = [ConfigMatplotlib.matplotlib_font]  # 配置中文字体
    fm.rcParams["axes.unicode_minus"] = False  # 解决负号变豆腐块
