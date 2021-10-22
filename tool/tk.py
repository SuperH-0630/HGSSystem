import tkinter as tk
from tkinter import font
from typing import List

import conf


def make_font(family: str = 'noto', **kwargs):
    return font.Font(family=conf.font_d[family], **kwargs)


def set_button_disable_from_list(btn_list: List[tk.Button], flat: str = 'disable'):
    for btn in btn_list:
        btn['state'] = flat
