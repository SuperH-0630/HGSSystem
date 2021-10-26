import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mysql_url", nargs=1, required=True, type=str, help="MySQL-URL")
parser.add_argument("--mysql_name", nargs=1, required=True, type=str, help="MySQL-用户名")
parser.add_argument("--mysql_passwd", nargs=1, required=True, type=str, help="MySQL-密码")

parser.add_argument("--program", nargs=1, required=True, type=str, choices=["setup",
                                                                            "garbage",
                                                                            "ranking",
                                                                            "manager",
                                                                            "ranking_website"],
                    help="选择启动的程序")

p_args = parser.parse_args()
