"""读取并展示图片的基础信息。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .loader import exif_orientation, open_image
from .utils import pad_display

# 常见颜色模式的中文说明；未列出的模式直接显示原始名称。
MODE_NAMES = {
    "1": "黑白二值图",
    "L": "灰度",
    "LA": "灰度 + 透明通道",
    "P": "调色板颜色",
    "RGB": "彩色",
    "RGBA": "彩色 + 透明通道",
    "CMYK": "印刷四色",
    "YCbCr": "视频色彩",
    "I": "32 位整数灰度",
    "I;16": "16 位整数灰度",
    "F": "32 位浮点灰度",
}

# EXIF 方向值对应的说明，用于提示手机照片的旋转情况。
ORIENTATION_NAMES = {
    2: "水平镜像",
    3: "旋转 180°",
    4: "垂直镜像",
    5: "顺时针旋转 90° 并镜像",
    6: "顺时针旋转 90°",
    7: "顺时针旋转 270° 并镜像",
    8: "顺时针旋转 270°",
}


@dataclass(frozen=True)
class ImageInfo:
    """一张图片的只读信息。"""

    path: Path
    filename: str
    format: str
    width: int
    height: int
    mode: str
    file_size: int
    orientation: int = 1

    @property
    def mode_text(self) -> str:
        """颜色模式的中文描述，例如 ``RGB 彩色``。"""
        return MODE_NAMES.get(self.mode, self.mode)

    @property
    def size_text(self) -> str:
        """文件大小，按 KB / MB 显示并保留两位小数。"""
        kb = self.file_size / 1024
        if kb >= 1024:
            return f"{kb / 1024:.2f} MB"
        return f"{kb:.2f} KB"

    @property
    def orientation_text(self) -> str:
        """EXIF 方向说明；方向正常时返回空字符串。"""
        return ORIENTATION_NAMES.get(self.orientation, "")


def read_image_info(path: str | Path) -> ImageInfo:
    """读取图片信息；读取失败时抛出 ImageToolError。"""
    p = Path(path).expanduser()
    image = open_image(p)
    file_size = p.stat().st_size

    info = ImageInfo(
        path=p.resolve(),
        filename=p.name,
        format=image.format or p.suffix.lstrip(".").upper(),
        width=image.width,
        height=image.height,
        mode=image.mode,
        file_size=file_size,
        orientation=exif_orientation(image),
    )
    image.close()
    return info


def print_image_info(info: ImageInfo) -> None:
    """以对齐的中文标签打印图片信息。"""
    rows = [
        ("文件名", info.filename),
        ("图片格式", info.format),
        ("尺寸", f"{info.width} × {info.height} 像素"),
        ("颜色模式", f"{info.mode}（{info.mode_text}）"),
        ("文件大小", info.size_text),
        ("文件路径", str(info.path)),
    ]
    if info.orientation_text:
        rows.append(("EXIF 方向", info.orientation_text + "，编辑时会自动校正"))

    print("图片信息")
    print("-" * 32)
    for label, value in rows:
        print(f"{pad_display(label, 10)}{value}")
