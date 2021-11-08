from .conf import conf_args


class ConfigCaptureRelease:
    """ 摄像头相关配置 """
    capture_num = tk_zoom = float(conf_args.get("capture_num", 1))  # 文字缩放  # 摄像头号
    capture_arg = []


ConfigCapture = ConfigCaptureRelease
