"""通用小工具。"""

from __future__ import annotations

import unicodedata


def char_width(char: str) -> int:
    """返回字符在等宽终端中占用的列数。

    中文、日文、韩文等全角字符占 2 列，其余占 1 列。
    """
    if unicodedata.east_asian_width(char) in ("W", "F", "A"):
        return 2
    return 1


def display_width(text: str) -> int:
    """返回字符串的显示宽度（以列为单位）。"""
    return sum(char_width(ch) for ch in text)


def pad_display(text: str, width: int) -> str:
    """按显示宽度在右侧补空格，使中英文混排也能对齐。"""
    padding = max(0, width - display_width(text))
    return text + " " * padding
