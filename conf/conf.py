import os
import sys

conf_path = os.path.dirname(os.path.abspath(sys.argv[0]))

try:
    with open(os.path.join(conf_path, "HGSSystem.conf.py"), "r", encoding='utf-8') as f:
        code = f.read()
        conf_args = {}
        exec(code, conf_args)
except Exception:
    conf_args = {}
