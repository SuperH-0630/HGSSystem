import tkinter as tk
from tkinter import font
from typing import List, Union

import conf

Disable_type = Union[tk.Button, tk.Entry]


def make_font(family: str = 'noto', **kwargs):
    return font.Font(family=conf.font_d[family], **kwargs)


def set_tk_disable_from_list(btn_list: List[Disable_type], flat: str = 'disable'):
    for btn in btn_list:
        btn['state'] = flat
