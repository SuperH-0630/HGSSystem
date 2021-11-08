"""
安装程序

1) 检查python版本
2) 复制文件到安装目录
3) 生成启动文件

"""
import os
import sys
import warnings
import shutil

if sys.version_info.major != 3:
    warnings.warn("请使用 Python3 运行程序")  # 使用 warning 确保 python2 可以输出提示
    exit(1)

if sys.version_info.minor < 9:
    warnings.warn("建议使用python3.9以上版本")

if len(sys.argv) == 1:
    print("请指定安装目录", file=sys.stderr)
    exit(1)

install_prefix = sys.argv[1]
if install_prefix.endswith(os.sep) or install_prefix.endswith('/'):
    install_prefix = os.path.join(install_prefix[:-1], "HGSSystem")
print(f"安装位置: {install_prefix}")
if input("[Y/n] ") != "Y":
    exit(1)

if len(sys.argv) == 2:
    install_prefix = sys.argv[1]
    install = ["garbage", "manager", "rank", "website"]
else:
    install = []
    for i in sys.argv[2:]:
        if i.lower() in ["garbage", "manager", "rank", "website"] and i not in install:
            install.append(i.lower())
    if len(install) == 0:
        install = ["garbage", "manager", "rank", "website"]

print(f"安装内容: {', '.join(install)}")
if input("[Y/n] ") != "Y":
    exit(1)


def check_make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)  # 创建目录


def delete(path):
    if os.path.isdir(path):
        print(f"删除目录: {path}")
        shutil.rmtree(path)
    elif os.path.isfile(path):
        print(f"删除文件: {path}")
        os.remove(path)


for i in os.listdir(install_prefix):
    if i in ['app', 'conf', 'core', 'equipment',
             'init.py', 'init.sql', 'LICENSE', 'main.py', 'README.md', 'sql', 'tk_ui', 'tool']:
        delete(os.path.join(install_prefix, i))

check_make_dir(install_prefix)
src = os.path.dirname(os.path.abspath(__file__))


def copy_file(src_path, dest_path):
    print(f"复制文件: {src_path} -> {dest_path}")
    shutil.copy(src_path, dest_path)


def copy_directory(src_path, dest_path):
    if not os.path.exists(dest_path):
        print(f"复制目录: {src_path} -> {dest_path}")
        shutil.copytree(src_path, dest_path)


def install_base():
    """
    安装基础部件
    tool包, conf包, Core包, MySQL包
    :return:
    """
    copy_file(os.path.join(src, "README.md"), os.path.join(install_prefix, "README.md"))
    copy_file(os.path.join(src, "LICENSE"), os.path.join(install_prefix, "LICENSE"))
    copy_file(os.path.join(src, "main.py"), os.path.join(install_prefix, "main.py"))
    copy_file(os.path.join(src, "init.py"), os.path.join(install_prefix, "init.py"))
    copy_file(os.path.join(src, "init.sql"), os.path.join(install_prefix, "init.sql"))

    copy_directory(os.path.join(src, "conf"), os.path.join(install_prefix, "conf"))
    copy_directory(os.path.join(src, "tool"), os.path.join(install_prefix, "tool"))
    copy_directory(os.path.join(src, "core"), os.path.join(install_prefix, "core"))
    copy_directory(os.path.join(src, "sql"), os.path.join(install_prefix, "sql"))


def install_website():
    copy_directory(os.path.join(src, "app"), os.path.join(install_prefix, "app"))


def install_garbage():
    copy_directory(os.path.join(src, "equipment"), os.path.join(install_prefix, "equipment"))
    check_make_dir(os.path.join(install_prefix, "tk_ui"))

    tk_ui_path = os.path.join(install_prefix, "tk_ui")
    copy_file(os.path.join(src, "tk_ui", "station.py"), os.path.join(tk_ui_path, "station.py"))
    copy_file(os.path.join(src, "tk_ui", "station_event.py"), os.path.join(tk_ui_path, "station_event.py"))
    copy_file(os.path.join(src, "tk_ui", "event.py"), os.path.join(tk_ui_path, "event.py"))


def install_rank():
    copy_directory(os.path.join(src, "equipment"), os.path.join(install_prefix, "equipment"))
    check_make_dir(os.path.join(install_prefix, "tk_ui"))

    tk_ui_path = os.path.join(install_prefix, "tk_ui")
    copy_file(os.path.join(src, "tk_ui", "ranking.py"), os.path.join(tk_ui_path, "ranking.py"))
    copy_file(os.path.join(src, "tk_ui", "event.py"), os.path.join(tk_ui_path, "event.py"))


def install_admin():
    copy_directory(os.path.join(src, "equipment"), os.path.join(install_prefix, "equipment"))
    check_make_dir(os.path.join(install_prefix, "tk_ui"))

    tk_ui_path = os.path.join(install_prefix, "tk_ui")
    copy_file(os.path.join(src, "tk_ui", "admin.py"), os.path.join(tk_ui_path, "admin.py"))
    copy_file(os.path.join(src, "tk_ui", "admin_event.py"), os.path.join(tk_ui_path, "admin_event.py"))
    copy_file(os.path.join(src, "tk_ui", "admin_program.py"), os.path.join(tk_ui_path, "admin_program.py"))
    copy_file(os.path.join(src, "tk_ui", "admin_menu.py"), os.path.join(tk_ui_path, "admin_menu.py"))
    copy_file(os.path.join(src, "tk_ui", "event.py"), os.path.join(tk_ui_path, "event.py"))


def install_venv():
    venv = os.path.join(install_prefix, 'venv')
    if not os.path.exists(venv):
        print(f"执行: {sys.executable} -m venv {venv}")
        os.system(f"{sys.executable} -m venv {venv}")
    suffix = os.path.splitext(sys.executable)[-1]
    for path, dirs, files in os.walk(venv):
        if f"python{suffix}" in files:
            return os.path.join(path, f"python{suffix}")
    return None


def run_init():
    init_py = os.path.join(install_prefix, "main.py")
    print(f"执行文件: {init_py}")
    os.system(f"{python} {init_py} --program setup")


def write_bat():
    main = os.path.join(install_prefix, "main.py")
    for i in ['setup'] + install:
        bat = os.path.join(install_prefix, f"{i}_HGSSystem.bat")
        print(f"创建批处理文件 {bat}")
        with open(bat, "w") as f:
            if i != "website":
                f.write(''' @echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin\n''')  # 隐藏 cmd 的命令
            f.write(f"{python} {main} --program {i} --run release")


def write_shell():
    main = os.path.join(install_prefix, "main.py")
    for i in ['setup'] + install:
        bat = os.path.join(install_prefix, f"{i}_HGSSystem.sh")
        print(f"创建shell脚本 {bat}")
        with open(bat, "w") as f:
            f.write(f"{python} {main} --program {i} --run release")


install_base()
for i in install:
    print(f"安装 {i} 系统 - 开始")
    if i == "garbage":
        install_garbage()
    elif i == "manager":
        install_admin()
    elif i == "rank":
        install_rank()
    elif i == 'website':
        install_website()
    print(f"安装 {i} 系统 - 完成")
python = install_venv()
if python is None:
    print("虚拟环境创建失败", file=sys.stderr)
    exit(1)
print(f"虚拟环境创建成功: {python}")
run_init()
if os.name == 'nt':
    write_bat()
elif os.name == 'posix':
    write_shell()

print("安装结束")
