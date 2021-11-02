from flask import Flask

from tool.login import create_uid
from sql.db import DB
from sql.user import find_user_by_name, find_user_by_id
from tool.type_ import *
from . import views


class WebUser:
    def __init__(self, name: uname_t, passwd: passwd_t = None, uid: uid_t = None):
        self._name = name
        if uid is None:
            self._uid = create_uid(name, passwd)
        else:
            self._uid = uid
        self.is_anonymous = False

    @property
    def name(self):
        return self._name

    @property
    def is_active(self):
        return views.auth_website.load_user_by_id(self._uid) is not None

    @property
    def is_authenticated(self):
        return views.auth_website.load_user_by_id(self._uid) is not None

    def get_id(self):
        return self._uid


class AuthWebsite:
    def __init__(self, app: Flask, db: DB):
        self._app = app
        self._db = db

    def load_user_by_name(self, name: uname_t, passwd: passwd_t) -> Optional[WebUser]:
        user = find_user_by_name(name, passwd, self._db)
        if user is None:
            return None
        return WebUser(name, uid=user.get_uid())

    def load_user_by_id(self, uid: uid_t) -> Optional[WebUser]:
        user = find_user_by_id(uid, self._db)
        if user is None:
            return None
        name = user.get_name()
        return WebUser(name, uid=uid)
