from . import args


class ConfigAliyunRelease:
    aliyun_key = args.p_args.aliyun_key[0]
    aliyun_secret = args.p_args.aliyun_secret[0]
    aliyun_region_id = "cn-shanghai"


ConfigAliyun = ConfigAliyunRelease
