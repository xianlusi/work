"""图片读取工具：统一处理文件校验、格式识别与 EXIF 方向。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from .errors import ImageToolError


def open_image(path: str | Path) -> Image.Image:
    """读取图片并返回脱离文件句柄的 Image 对象。

    参数:
        path: 图片路径。

    异常:
        ImageToolError: 文件不存在、不是文件或不是有效图片时抛出。
    """
    p = Path(path).expanduser()

    if not p.exists():
        raise ImageToolError(f"文件不存在：{p}")
    if not p.is_file():
        raise ImageToolError(f"路径不是文件：{p}")

    try:
        with Image.open(p) as im:
            im.load()  # 立即解码，避免后续操作时文件已被关闭
            image = im.copy()
            image.format = im.format
    except UnidentifiedImageError:
        raise ImageToolError(f"不是有效的图片文件：{p}") from None
    except (OSError, ValueError) as exc:
        raise ImageToolError(f"无法读取图片：{p}（{exc}）") from None

    return image


def apply_exif_orientation(image: Image.Image) -> Image.Image:
    """按照 EXIF 方向信息把图片摆正（手机照片常见）。

    没有方向信息时原样返回。
    """
    return ImageOps.exif_transpose(image)


def exif_orientation(image: Image.Image) -> int:
    """返回 EXIF 方向值，默认为 1（正常方向）。"""
    try:
        return int(image.getexif().get(0x0112, 1))
    except (AttributeError, TypeError, ValueError):
        return 1
