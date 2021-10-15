from .type_ import *
import hashlib
import conf
from random import randint


def creat_uid(name: uname_t, passwd: passwd_t, salt: str = conf.passwd_salt) -> str:
    return hashlib.md5(f"HGSSystem-USER{name}-PASSWORD:{passwd}-{salt}-END".encode('utf-8')).hexdigest()


def check_login(uid: uid_t, name: uname_t, passwd: passwd_t, salt: str = conf.passwd_salt) -> bool:
    return uid == creat_uid(name, passwd, salt)


def randomPassword():
    passwd_char = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890<>,.?/:;''!@#$%^&*()-_=+*'
    passwd = []
    for i in range(randint(16, 22)):
        passwd.append(passwd_char[randint(0, len(passwd_char) - 1)])
    return "".join(passwd)
