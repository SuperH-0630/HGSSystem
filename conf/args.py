import argparse
import os
import sys
from typing import Optional

res = os.environ.get('HGSSystem_NA')
p_args: dict[str: Optional[str]] = {"mysql_url": None,
                                    "mysql_name": None,
                                    "mysql_passwd": None,
                                    "mysql_port": None,
                                    "aliyun_key": None,
                                    "aliyun_secret": None,
                                    "program": None,
                                    "run": None}

if res is None or res == "False":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql_url", nargs=1, type=str, help="MySQL-URL")
    parser.add_argument("--mysql_name", nargs=1, type=str, help="MySQL-用户名")
    parser.add_argument("--mysql_passwd", nargs=1, type=str, help="MySQL-密码")
    parser.add_argument("--mysql_port", nargs=1, type=str, help="MySQL-端口")

    parser.add_argument("--aliyun_key", nargs=1, type=str, help="阿里云认证-KET")
    parser.add_argument("--aliyun_secret", nargs=1, type=str, help="阿里云认证-SECRET")

    parser.add_argument("--program", nargs=1, type=str, choices=["setup",
                                                                 "garbage",
                                                                 "ranking",
                                                                 "manager",
                                                                 "website"],
                        help="选择启动的程序")

    parser.add_argument("--run_type", nargs=1, type=str, choices=["test",
                                                                  "release"],
                        default=["release"],
                        help="选择允许模式")

    p_args_ = parser.parse_args()
    if p_args_.mysql_url is not None:
        p_args['mysql_url'] = p_args_.mysql_url[0]
    if p_args_.mysql_name is not None:
        p_args['mysql_name'] = p_args_.mysql_name[0]
    if p_args_.mysql_passwd is not None:
        p_args['mysql_passwd'] = p_args_.mysql_passwd[0]
    if p_args_.mysql_port is not None:
        p_args['mysql_port'] = p_args_.mysql_port[0]

    if p_args_.aliyun_key is not None:
        p_args['aliyun_key'] = p_args_.aliyun_key[0]
    if p_args_.aliyun_secret is not None:
        p_args['aliyun_secret'] = p_args_.aliyun_secret[0]

    if p_args_.program is not None:
        p_args['program'] = p_args_.program[0].lower()
    if p_args_.run_type is not None:
        p_args['run'] = p_args_.run_type[0].lower()

if p_args.get('program') is None:
    res = os.environ.get('HGSSystem_Program')
    if res is None:
        print("未指定启动程序")
        exit(1)
    p_args['program'] = res

if p_args.get('mysql_url') is None or p_args.get('mysql_name') is None or p_args.get('mysql_passwd') is None:
    res = os.environ.get('HGSSystem_MySQL')
    if res is not None:
        res = res.split(';')
        if len(res) == 4:
            p_args['mysql_url'] = res[0]
            p_args['mysql_name'] = res[1]
            p_args['mysql_passwd'] = res[2]
            p_args['mysql_port'] = res[3]
        elif len(res) == 3:
            p_args['mysql_url'] = res[0]
            p_args['mysql_name'] = res[1]
            p_args['mysql_passwd'] = res[2]
            p_args['mysql_port'] = ""
        else:
            print("MYSQL地址错误", file=sys.stderr)
            exit(1)

if p_args.get('aliyun_key') is None or p_args.get('aliyun_secret') is None:
    res = os.environ.get('HGSSystem_Aliyun')
    if res is not None:
        res = res.split(';')
        if len(res) == 2:
            p_args["aliyun_key"] = res[0]
            p_args["aliyun_secret"] = res[1]
        else:
            print("阿里云认证错误", file=sys.stderr)
            exit(1)

if p_args.get('run') is None:
    res = os.environ.get('HGSSystem_Run')
    if res is not None:
        p_args['run'] = res.lower()
    else:
        p_args['run'] = "release"
