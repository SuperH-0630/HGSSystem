# import tkinter as tk
# import tkinter.font as font
#
# from tool.type_ import *
#
# from sql.db import DB
# from sql.user import creat_new_user
# from sql.garbage import creat_new_garbage
#
# from equipment.scan_user import write_uid_qr, write_all_uid_qr
# from equipment.scan_garbage import write_gid_qr
#
# from core.user import User
# from core.garbage import GarbageBag
#
#
# class AdminStationException:
#     ...
#
#
# class ControlNotLogin(AdminStationException):
#     ...
#
#
# class CreatGarbageError(AdminStationException):
#     ...
#
#
# class CreatUserError(AdminStationException):
#     ...
#
#
# class AdminStationStatus:
#     def __init__(self,
#                  win,
#                  db: DB):
#         self._win = win
#         self._db: DB = db
#         self._admin: Optional[User] = None  # 操作者
#
#     def __check_manager_user(self):
#         if self._admin is None or not self._admin.is_manager():
#             raise ControlNotLogin
#
#     def creat_garbage(self, path: str, num: int = 1) -> List[tuple[str, Optional[GarbageBag]]]:
#         self.__check_manager_user()
#
#         re = []
#         for _ in range(num):
#             gar = creat_new_garbage(self._db)
#             if gar is None:
#                 raise CreatGarbageError
#             res = write_gid_qr(gar.get_gid(), path, self._db)
#             re.append(res)
#         return re
#
#     def creat_user(self, name: uname_t, passwd: passwd_t, phone: str, manager: bool) -> Optional[User]:
#         user = creat_new_user(name, passwd, phone, manager, self._db)
#         if user is None:
#             raise CreatUserError
#         return user
#
#     def creat_user_from_list(self, user_list: List[Tuple[uname_t, passwd_t, str]], manager: bool) -> List[User]:
#         re = []
#         for i in user_list:
#             user = creat_new_user(i[0], i[1], i[2], manager, self._db)
#             if user is None:
#                 raise CreatUserError
#             re.append(user)
#         return re
#
#     def get_uid_qrcode(self, uid: uid_t, path: str) -> Tuple[str, Optional[User]]:
#         return write_uid_qr(uid, path, self._db)
#
#     def get_uid_qrcode_from_list(self, uid_list: List[uid_t], path: str) -> List[Tuple[str, Optional[User]]]:
#         re = []
#         for uid in uid_list:
#             res = write_uid_qr(uid, path, self._db)
#             re.append(res)
#         return re
#
#     def get_all_uid_qrcode(self, path: str, where: str = "") -> List[str]:
#         return write_all_uid_qr(path, self._db, where=where)
#
#
# class AdminStation:
#     def __init__(self, db: DB):
#         self._status = AdminStationStatus(self, db)
#
#         self._window = tk.Tk()
#         self._sys_height = self._window.winfo_screenheight()
#         self._sys_width = self._window.winfo_screenwidth()
#
#         self._win_height = int(self._sys_height * (2 / 3))
#         self._win_width = int(self._sys_width * (1 / 3))
#         self._full_screen = False
