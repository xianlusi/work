"""保存逻辑的单元测试。"""

from __future__ import annotations

import unittest

from PIL import Image

from imagetool.errors import ImageToolError
from imagetool.saver import default_output_path, has_alpha, save_image

from .helpers import cleanup_temp, make_rgb, make_rgba, temp_dir


class DefaultPathTests(unittest.TestCase):
    def test_keeps_extension(self) -> None:
        result = default_output_path("images/demo.jpg", "resized")
        self.assertEqual(result.name, "demo_resized.jpg")
        self.assertEqual(result.parent.name, "images")

    def test_custom_extension(self) -> None:
        result = default_output_path("images/demo.jpg", "gray", ".png")
        self.assertEqual(result.name, "demo_gray.png")

    def test_no_extension(self) -> None:
        result = default_output_path("images/demo", "gray")
        self.assertEqual(result.name, "demo_gray.png")


class SaveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = temp_dir()
        self.addCleanup(cleanup_temp, self.root)
        self.source = self.root / "source.png"
        make_rgb().save(self.source)

    def test_saves_jpeg(self) -> None:
        target = self.root / "out.jpg"
        saved = save_image(make_rgb(), target, source_path=self.source)
        self.assertTrue(saved.exists())
        with Image.open(saved) as image:
            self.assertEqual(image.format, "JPEG")

    def test_refuses_to_overwrite_source(self) -> None:
        with self.assertRaises(ImageToolError):
            save_image(make_rgb(), self.source, source_path=self.source)

    def test_refuses_existing_file(self) -> None:
        target = self.root / "out.png"
        target.write_bytes(b"x")
        with self.assertRaises(ImageToolError):
            save_image(make_rgb(), target, source_path=self.source)

    def test_force_overwrites(self) -> None:
        target = self.root / "out.png"
        target.write_bytes(b"x")
        save_image(make_rgb(), target, source_path=self.source, force=True)
        with Image.open(target) as image:
            self.assertEqual(image.size, (120, 80))

    def test_unsupported_extension(self) -> None:
        with self.assertRaises(ImageToolError):
            save_image(make_rgb(), self.root / "out.gif", source_path=self.source)

    def test_creates_parent_directory(self) -> None:
        target = self.root / "nested" / "out.png"
        save_image(make_rgb(), target, source_path=self.source)
        self.assertTrue(target.exists())

    def test_rgba_to_jpeg_gets_white_background(self) -> None:
        target = self.root / "logo.jpg"
        save_image(make_rgba(), target, source_path=self.source)
        with Image.open(target) as image:
            self.assertEqual(image.mode, "RGB")
            pixel = image.getpixel((0, 0))
            self.assertTrue(all(channel >= 245 for channel in pixel), pixel)


class AlphaTests(unittest.TestCase):
    def test_rgba_has_alpha(self) -> None:
        self.assertTrue(has_alpha(make_rgba()))

    def test_rgb_has_no_alpha(self) -> None:
        self.assertFalse(has_alpha(make_rgb()))


if __name__ == "__main__":
    unittest.main()
