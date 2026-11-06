"""图片信息读取的单元测试。"""

from __future__ import annotations

import unittest
from pathlib import Path

from PIL import Image

from imagetool.errors import ImageToolError
from imagetool.info import ImageInfo, read_image_info

from .helpers import cleanup_temp, make_rgb, make_rgba, temp_dir


class ReadInfoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = temp_dir()
        self.addCleanup(cleanup_temp, self.root)

    def test_jpeg_info(self) -> None:
        path = self.root / "photo.jpg"
        make_rgb(320, 200).save(path, quality=90)

        info = read_image_info(path)

        self.assertEqual(info.filename, "photo.jpg")
        self.assertEqual(info.format, "JPEG")
        self.assertEqual((info.width, info.height), (320, 200))
        self.assertEqual(info.mode, "RGB")
        self.assertGreater(info.file_size, 0)

    def test_png_alpha_mode_text(self) -> None:
        path = self.root / "logo.png"
        make_rgba(40, 30).save(path)

        info = read_image_info(path)

        self.assertEqual(info.mode, "RGBA")
        self.assertIn("透明通道", info.mode_text)

    def test_missing_file(self) -> None:
        with self.assertRaises(ImageToolError):
            read_image_info(self.root / "missing.jpg")

    def test_not_an_image(self) -> None:
        path = self.root / "notes.txt"
        path.write_text("hello", encoding="utf-8")
        with self.assertRaises(ImageToolError):
            read_image_info(path)

    def test_directory(self) -> None:
        with self.assertRaises(ImageToolError):
            read_image_info(self.root)


class SizeFormatTests(unittest.TestCase):
    def _info(self, size: int) -> ImageInfo:
        return ImageInfo(
            path=Path("demo.jpg"),
            filename="demo.jpg",
            format="JPEG",
            width=10,
            height=10,
            mode="RGB",
            file_size=size,
        )

    def test_kilobytes(self) -> None:
        self.assertEqual(self._info(2048).size_text, "2.00 KB")

    def test_megabytes(self) -> None:
        self.assertEqual(self._info(2 * 1024 * 1024).size_text, "2.00 MB")

    def test_two_decimals(self) -> None:
        self.assertEqual(self._info(1500).size_text, "1.46 KB")


if __name__ == "__main__":
    unittest.main()
