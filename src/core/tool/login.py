from .type_ import *
import hashlib


def check_login(uid: uid_t, name: uname_t, passwd: passwd_t, salt: str) -> bool:
    ...
