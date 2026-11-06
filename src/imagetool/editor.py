"""图片编辑操作：缩放、裁剪、旋转、翻转、灰度化、格式转换。

每个函数接收一个 PIL.Image，返回处理后的新对象，不修改原图。
参数不合法时抛出 ImageToolError，由命令行入口统一提示。
"""

from __future__ import annotations

from PIL import Image

from .errors import ImageToolError

# 顺时针旋转角度与 Pillow 变换的对应关系
_ROTATE_TRANSFORMS = {
    90: Image.Transpose.ROTATE_270,   # 逆时针 270° = 顺时针 90°
    180: Image.Transpose.ROTATE_180,
    270: Image.Transpose.ROTATE_90,   # 逆时针 90° = 顺时针 270°
}

_FLIP_TRANSFORMS = {
    "horizontal": Image.Transpose.FLIP_LEFT_RIGHT,
    "vertical": Image.Transpose.FLIP_TOP_BOTTOM,
}


def resize_image(
    image: Image.Image, width: int | None = None, height: int | None = None
) -> Image.Image:
    """缩放图片。

    - 同时给出宽高：按指定尺寸缩放（可能改变宽高比）。
    - 只给宽或高：另一边按原图比例计算。
    """
    if width is None and height is None:
        raise ImageToolError("请至少指定宽度（--width）或高度（--height）中的一个。")
    if width is not None and width <= 0:
        raise ImageToolError(f"宽度必须是大于 0 的整数，当前为 {width}。")
    if height is not None and height <= 0:
        raise ImageToolError(f"高度必须是大于 0 的整数，当前为 {height}。")

    if width is None:
        width = round(image.width * height / image.height)  # type: ignore[operator]
    if height is None:
        height = round(image.height * width / image.width)

    width = max(1, int(width))
    height = max(1, int(height))

    if (width, height) == image.size:
        return image.copy()
    return image.resize((width, height), Image.Resampling.LANCZOS)


def crop_image(
    image: Image.Image, left: int, top: int, right: int, bottom: int
) -> Image.Image:
    """按矩形区域裁剪，坐标为像素，右/下边界不包含在结果内。"""
    width, height = image.size

    if right <= left or bottom <= top:
        raise ImageToolError(
            f"裁剪区域无效：右边界必须大于左边界、下边界必须大于上边界（当前 {left},{top},{right},{bottom}）。"
        )
    if left < 0 or top < 0 or right > width or bottom > height:
        raise ImageToolError(
            f"裁剪区域超出图片范围：图片尺寸为 {width} × {height} 像素，"
            f"坐标需满足 0 ≤ left < right ≤ {width}、0 ≤ top < bottom ≤ {height}。"
        )

    return image.crop((left, top, right, bottom))


def rotate_image(image: Image.Image, angle: int) -> Image.Image:
    """按顺时针方向旋转 90、180 或 270 度，画布自动扩展。"""
    if angle not in _ROTATE_TRANSFORMS:
        raise ImageToolError(f"旋转角度只支持 90、180、270 度，当前为 {angle}。")
    return image.transpose(_ROTATE_TRANSFORMS[angle])


def flip_image(image: Image.Image, direction: str) -> Image.Image:
    """翻转图片：horizontal 为左右镜像，vertical 为上下镜像。"""
    key = direction.lower()
    if key not in _FLIP_TRANSFORMS:
        raise ImageToolError(
            f"翻转方向只支持 horizontal（水平翻转）或 vertical（垂直翻转），当前为 {direction}。"
        )
    return image.transpose(_FLIP_TRANSFORMS[key])


def grayscale_image(image: Image.Image) -> Image.Image:
    """把图片转换为 8 位灰度图。

    已经是灰度模式时返回副本；带透明通道的图片会丢失透明信息。
    """
    if image.mode in ("L", "1", "I", "I;16", "F"):
        return image.copy()
    return image.convert("L")
