"""命令行界面。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from . import __version__
from .editor import (
    crop_image,
    flip_image,
    grayscale_image,
    resize_image,
    rotate_image,
)
from .errors import ImageToolError
from .info import print_image_info, read_image_info
from .loader import apply_exif_orientation, open_image
from .saver import default_output_path, has_alpha, save_image

EPILOG = """\
示例：
  imagetool info samples/demo.jpg
  imagetool resize samples/demo.jpg --width 320
  imagetool crop samples/demo.jpg -l 40 -t 40 -r 600 -b 440
  imagetool rotate samples/demo.jpg --angle 90
  imagetool flip samples/demo.jpg --direction vertical
  imagetool gray samples/logo.png
  imagetool convert samples/logo.png --format jpg
"""


def build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="imagetool",
        description="查看图片信息，并对图片做缩放、裁剪、旋转、翻转、灰度化和格式转换。",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="命令")

    # info：查看图片信息
    p_info = subparsers.add_parser(
        "info",
        help="查看图片基础信息",
        description="查看图片的文件名、格式、宽高、颜色模式和文件大小。",
    )
    p_info.add_argument("image", help="图片路径，例如 samples/demo.jpg")

    # resize：缩放
    p_resize = subparsers.add_parser(
        "resize",
        help="缩放图片",
        description="按指定宽高缩放；只给宽度或高度时，另一边按原比例自动计算。",
    )
    p_resize.add_argument("image", help="图片路径")
    p_resize.add_argument("-w", "--width", type=int, help="目标宽度（像素）")
    p_resize.add_argument("-H", "--height", type=int, help="目标高度（像素）")
    _add_output_args(p_resize)

    # crop：裁剪
    p_crop = subparsers.add_parser(
        "crop",
        help="裁剪图片",
        description="按左、上、右、下四个坐标裁剪；右/下边界不包含在结果内。",
    )
    p_crop.add_argument("image", help="图片路径")
    p_crop.add_argument("-l", "--left", type=int, required=True, help="左边界 x 坐标")
    p_crop.add_argument("-t", "--top", type=int, required=True, help="上边界 y 坐标")
    p_crop.add_argument("-r", "--right", type=int, required=True, help="右边界 x 坐标（不包含）")
    p_crop.add_argument("-b", "--bottom", type=int, required=True, help="下边界 y 坐标（不包含）")
    _add_output_args(p_crop)

    # rotate：旋转
    p_rotate = subparsers.add_parser(
        "rotate", help="旋转图片", description="按顺时针方向旋转 90、180 或 270 度。"
    )
    p_rotate.add_argument("image", help="图片路径")
    p_rotate.add_argument(
        "-a", "--angle", type=int, choices=(90, 180, 270), required=True, help="顺时针旋转角度"
    )
    _add_output_args(p_rotate)

    # flip：翻转
    p_flip = subparsers.add_parser(
        "flip", help="翻转图片", description="水平翻转（左右镜像）或垂直翻转（上下镜像）。"
    )
    p_flip.add_argument("image", help="图片路径")
    p_flip.add_argument(
        "-d",
        "--direction",
        choices=("horizontal", "vertical"),
        default="horizontal",
        help="翻转方向，默认 horizontal",
    )
    _add_output_args(p_flip)

    # gray：灰度化
    p_gray = subparsers.add_parser(
        "gray", help="灰度化", description="把彩色图片转换为灰度图，结果保存为 PNG。"
    )
    p_gray.add_argument("image", help="图片路径")
    _add_output_args(p_gray)

    # convert：格式转换
    p_convert = subparsers.add_parser(
        "convert",
        help="格式转换",
        description="在 PNG 与 JPG 之间转换；带透明通道的图片转 JPG 时会自动填充白色背景。",
    )
    p_convert.add_argument("image", help="图片路径")
    p_convert.add_argument(
        "-f", "--format", choices=("png", "jpg"), required=True, help="目标格式"
    )
    _add_output_args(p_convert)

    return parser


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    """为需要保存文件的子命令添加公共参数。"""
    parser.add_argument(
        "-o", "--output", help="输出文件路径（默认：与原图同目录，文件名加后缀）"
    )
    parser.add_argument("--force", action="store_true", help="输出文件已存在时覆盖")


def _load_for_edit(path: str) -> Image.Image:
    """读取图片并按 EXIF 方向摆正，供编辑命令使用。"""
    image = open_image(path)
    oriented = apply_exif_orientation(image)
    if oriented is not image:
        image.close()
    return oriented


def _display_path(path: Path) -> str:
    """输出路径尽量显示为相对当前目录的形式，便于阅读。"""
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _save_result(
    args: argparse.Namespace,
    image: Image.Image,
    suffix: str,
    extension: str | None = None,
) -> Path:
    """保存编辑结果，并打印保存位置与新尺寸。"""
    output = args.output or default_output_path(args.image, suffix, extension)
    saved = save_image(image, output, source_path=args.image, force=args.force)
    print(f"已保存：{_display_path(saved)}")
    print(f"尺寸：{image.width} × {image.height} 像素（原图未修改）")
    return saved


def _run_edit(args: argparse.Namespace) -> int:
    """执行编辑类子命令并保存结果。"""
    image = _load_for_edit(args.image)

    if args.command == "resize":
        result = resize_image(image, args.width, args.height)
        _save_result(args, result, "resized")
    elif args.command == "crop":
        result = crop_image(image, args.left, args.top, args.right, args.bottom)
        _save_result(args, result, "cropped")
    elif args.command == "rotate":
        result = rotate_image(image, args.angle)
        _save_result(args, result, "rotated")
    elif args.command == "flip":
        result = flip_image(image, args.direction)
        _save_result(args, result, "flipped")
    elif args.command == "gray":
        if image.mode in ("L", "1", "I", "I;16", "F"):
            print("提示：原图已经是灰度图，将保存一份副本。")
        elif has_alpha(image):
            print("提示：原图包含透明通道，灰度化后透明信息会丢失。")
        result = grayscale_image(image)
        _save_result(args, result, "gray", ".png")
    elif args.command == "convert":
        if args.format == "jpg" and has_alpha(image):
            print("提示：原图包含透明通道，已用白色背景填充后保存为 JPG。")
        ext = ".png" if args.format == "png" else ".jpg"
        source = Path(args.image).expanduser()
        output = args.output or source.with_suffix(ext)
        result = image
        saved = save_image(result, output, source_path=args.image, force=args.force)
        print(f"已保存：{_display_path(saved)}")
        print(f"尺寸：{result.width} × {result.height} 像素（原图未修改）")
    else:
        raise ImageToolError(f"未知命令：{args.command}")

    image.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    """程序入口，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "info":
            print_image_info(read_image_info(args.image))
            return 0
        return _run_edit(args)
    except ImageToolError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130
    except BrokenPipeError:
        return 1
