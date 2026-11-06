"""测试用的图片构造工具。"""

from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path

from PIL import Image


def temp_dir() -> Path:
    """创建测试用临时目录。

    不使用 tempfile.TemporaryDirectory：它在 Windows 上会以 0700 权限创建目录，
    在部分受限环境中后续写入会被拒绝。这里用默认权限创建，并配合 cleanup_temp 清理。
    """
    path = Path(tempfile.gettempdir()) / f"imagetool-test-{uuid.uuid4().hex[:10]}"
    path.mkdir()
    return path


def cleanup_temp(path: Path) -> None:
    """尽力删除临时目录，不因清理失败而让测试报错。"""
    shutil.rmtree(path, ignore_errors=True)



def make_rgb(width: int = 120, height: int = 80) -> Image.Image:
    """构造一张左右上下颜色不同的 RGB 图，方便验证翻转方向。"""
    image = Image.new("RGB", (width, height), (255, 0, 0))
    for y in range(height):
        for x in range(width):
            if x >= width // 2 and y < height // 2:
                image.putpixel((x, y), (0, 255, 0))   # 右上：绿
            elif x < width // 2 and y >= height // 2:
                image.putpixel((x, y), (0, 0, 255))   # 左下：蓝
            elif x >= width // 2 and y >= height // 2:
                image.putpixel((x, y), (255, 255, 0))  # 右下：黄
    return image


def make_rgba(width: int = 40, height: int = 30) -> Image.Image:
    """构造一张四角透明的 RGBA 图。"""
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height // 2, height):
        for x in range(width // 2, width):
            image.putpixel((x, y), (200, 30, 30, 255))
    return image
