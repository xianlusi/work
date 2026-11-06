"""命令行界面。"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .errors import ImageToolError
from .info import print_image_info, read_image_info


def build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="imagetool",
        description="查看图片信息，并对图片做缩放、裁剪、旋转、翻转、灰度化和格式转换。",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="命令")

    # info：查看图片信息
    p_info = subparsers.add_parser(
        "info", help="查看图片基础信息", description="查看图片的文件名、格式、宽高、颜色模式和文件大小。"
    )
    p_info.add_argument("image", help="图片路径，例如 samples/demo.jpg")

    return parser


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
    except ImageToolError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130

    parser.print_help()
    return 2
