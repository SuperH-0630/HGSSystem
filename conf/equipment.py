from .conf import conf_args


class ConfigCaptureRelease:
    """ 摄像头相关配置 """
    use_opencv = bool(conf_args.get("use_opencv", True))
    capture_num = tk_zoom = float(conf_args.get("capture_num", 1))  # 摄像头号
    capture_arg = []


ConfigCapture = ConfigCaptureRelease
