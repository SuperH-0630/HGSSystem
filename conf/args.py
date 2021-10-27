import argparse
import os
import warnings

parser = argparse.ArgumentParser()
parser.add_argument("--mysql_url", nargs=1, required=False, type=str, default=None, help="MySQL-URL")
parser.add_argument("--mysql_name", nargs=1, required=False, type=str, default=None, help="MySQL-用户名")
parser.add_argument("--mysql_passwd", nargs=1, required=False, type=str, default=None, help="MySQL-密码")
parser.add_argument("--mysql_port", nargs=1, required=False, type=str, default=[None], help="MySQL-端口")

parser.add_argument("--aliyun_key", nargs=1, required=False, type=str, default=None, help="阿里云认证-KET")
parser.add_argument("--aliyun_secret", nargs=1, required=False, type=str, default=None, help="阿里云认证-SECRET")

parser.add_argument("--program", nargs=1, required=True, type=str, choices=["setup",
                                                                            "garbage",
                                                                            "ranking",
                                                                            "manager",
                                                                            "ranking_website"],
                    help="选择启动的程序")

parser.add_argument("--run", nargs=1, required=False, type=str, choices=["Test",
                                                                         "Release"],
                    default=["Release"],
                    help="选择允许模式")

p_args = parser.parse_args()

if p_args.mysql_url is None or p_args.mysql_name is None or p_args.mysql_passwd is None:
    res = os.environ.get('HGSSystem_MySQL')
    if res is None:
        warnings.warn("未找到MySQL地址")
        exit(1)
    res = res.split(';')
    if len(res) == 4:
        p_args.mysql_url = [res[0]]
        p_args.mysql_name = [res[1]]
        p_args.mysql_passwd = [res[2]]
        p_args.mysql_port = [res[3]]
    elif len(res) == 3:
        p_args.mysql_url = [res[0]]
        p_args.mysql_name = [res[1]]
        p_args.mysql_passwd = [res[2]]
        p_args.mysql_port = [None]
    else:
        warnings.warn("MYSQL地址错误")
        exit(1)

if p_args.aliyun_key is None or p_args.aliyun_secret is None:
    res = os.environ.get('HGSSystem_Aliyun')
    if res is None:
        warnings.warn("未找到阿里云认证")
        exit(1)
    res = res.split(';')
    if len(res) == 2:
        p_args.aliyun_key = [res[0]]
        p_args.aliyun_secret = [res[1]]
    else:
        warnings.warn("阿里云认证错误")
        exit(1)
