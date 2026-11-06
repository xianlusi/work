"""保存图片：统一处理输出路径、格式与 JPG 透明通道问题。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from .errors import ImageToolError

# 允许的输出扩展名 -> Pillow 保存格式
OUTPUT_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".bmp": "BMP",
    ".webp": "WEBP",
    ".tif": "TIFF",
    ".tiff": "TIFF",
}


def default_output_path(source: str | Path, suffix: str, extension: str | None = None) -> Path:
    """生成默认输出路径，例如 demo.jpg -> demo_resized.jpg。"""
    source_path = Path(source).expanduser()
    ext = extension or source_path.suffix or ".png"
    return source_path.with_name(f"{source_path.stem}_{suffix}{ext}")


def has_alpha(image: Image.Image) -> bool:
    """判断图片是否包含透明通道（含调色板透明色）。"""
    return image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )


def flatten_to_rgb(image: Image.Image, background: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """把带透明通道的图片合成到纯色背景上并转为 RGB。"""
    if image.mode == "P":
        image = image.convert("RGBA")
    if image.mode in ("RGBA", "LA"):
        rgba = image.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, background)
        canvas.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
        return canvas
    return image.convert("RGB")


def save_image(
    image: Image.Image,
    output_path: str | Path,
    source_path: str | Path | None = None,
    force: bool = False,
) -> Path:
    """保存图片并返回最终绝对路径。

    参数:
        image: 待保存的图片。
        output_path: 输出文件路径，扩展名决定格式。
        source_path: 原图路径；用于阻止覆盖原图。
        force: 输出文件已存在时是否覆盖。
    """
    out = Path(output_path).expanduser()
    fmt = OUTPUT_FORMATS.get(out.suffix.lower())
    if fmt is None:
        supported = "、".join(sorted(OUTPUT_FORMATS))
        raise ImageToolError(f"不支持的输出格式“{out.suffix or '无扩展名'}”，可用格式：{supported}。")

    if source_path is not None:
        source = Path(source_path).expanduser().resolve()
        if out.resolve() == source:
            raise ImageToolError("输出路径与原图相同；程序不会覆盖原图，请指定其他输出文件名。")

    if out.exists() and not force:
        raise ImageToolError(f"输出文件已存在：{out}；如需覆盖请加 --force。")

    save_kwargs: dict[str, object] = {}
    if fmt == "JPEG":
        if image.mode not in ("RGB", "L"):
            image = flatten_to_rgb(image)
        save_kwargs = {"quality": 92, "subsampling": 0}
    elif fmt == "PNG":
        if image.mode == "CMYK":
            image = image.convert("RGB")
        save_kwargs = {"optimize": True}

    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        image.save(out, format=fmt, **save_kwargs)
    except (OSError, ValueError) as exc:
        raise ImageToolError(f"保存失败：{out}（{exc}）") from None

    return out.resolve()
