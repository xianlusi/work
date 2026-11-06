"""命令行入口的测试：退出码、提示信息与默认输出路径。"""

from __future__ import annotations

import contextlib
import io
import unittest

from PIL import Image

from imagetool.cli import main

from .helpers import cleanup_temp, make_rgb, make_rgba, temp_dir


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = temp_dir()
        self.addCleanup(cleanup_temp, self.root)
        self.source = self.root / "demo.jpg"
        make_rgb(200, 100).save(self.source, quality=90)

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_info(self) -> None:
        code, out, err = self.run_cli("info", str(self.source))
        self.assertEqual(code, 0)
        self.assertIn("文件名", out)
        self.assertIn("demo.jpg", out)
        self.assertEqual(err, "")

    def test_info_missing_file(self) -> None:
        code, out, err = self.run_cli("info", str(self.root / "missing.jpg"))
        self.assertEqual(code, 1)
        self.assertIn("错误", err)
        self.assertEqual(out, "")

    def test_resize_writes_default_name(self) -> None:
        code, out, _ = self.run_cli("resize", str(self.source), "-w", "100")
        self.assertEqual(code, 0)
        target = self.root / "demo_100x50.jpg"
        self.assertTrue(target.exists())
        self.assertIn(str(target.resolve()), out)
        with Image.open(target) as image:
            self.assertEqual(image.size, (100, 50))

    def test_resize_invalid_width(self) -> None:
        code, _, err = self.run_cli("resize", str(self.source), "-w", "0")
        self.assertEqual(code, 1)
        self.assertIn("宽度", err)

    def test_gray_reports_existing_grayscale(self) -> None:
        gray_path = self.root / "gray.png"
        Image.new("L", (20, 20), 128).save(gray_path)
        code, out, _ = self.run_cli("gray", str(gray_path))
        self.assertEqual(code, 0)
        self.assertIn("已经是灰度图", out)

    def test_convert_alpha_to_jpg_prints_notice(self) -> None:
        logo = self.root / "logo.png"
        make_rgba().save(logo)
        code, out, _ = self.run_cli("convert", str(logo), "-f", "jpg")
        self.assertEqual(code, 0)
        self.assertIn("透明通道", out)
        with Image.open(self.root / "logo.jpg") as image:
            self.assertEqual(image.mode, "RGB")

    def test_no_command_prints_help(self) -> None:
        code, out, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("用法", out.replace("usage", "用法"))


if __name__ == "__main__":
    unittest.main()
