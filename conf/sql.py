import sys
import warnings

if len(sys.argv) != 4:
    warnings.warn(f"参数不足: {len(sys.argv)}")
    raise exit(1)

database = 'MySQL'
mysql_url = sys.argv[1]
mysql_name = sys.argv[2]
mysql_passwd = sys.argv[3]
