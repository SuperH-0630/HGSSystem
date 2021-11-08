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
    if ConfigMatplotlib.matplotlib_font not in [f.name for f in fm.fontManager.ttflist]:
        print(f"请安装 {ConfigMatplotlib.matplotlib_font} 字体")
    fm.rcParams["font.sans-serif"] = [ConfigMatplotlib.matplotlib_font]  # 配置中文字体
    fm.rcParams["axes.unicode_minus"] = False  # 解决负号变豆腐块
