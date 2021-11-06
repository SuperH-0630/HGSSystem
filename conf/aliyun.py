from . import args


class ConfigAliyunRelease:
    """ 阿里云 SDK 相关配置 """
    aliyun_key = args.p_args['aliyun_key']
    aliyun_secret = args.p_args['aliyun_secret']
    aliyun_region_id = "cn-shanghai"


ConfigAliyun = ConfigAliyunRelease
