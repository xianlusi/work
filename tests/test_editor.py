"""编辑功能的单元测试。"""

from __future__ import annotations

import unittest

from PIL import Image

from imagetool.editor import (
    crop_image,
    flip_image,
    grayscale_image,
    resize_image,
    rotate_image,
)
from imagetool.errors import ImageToolError

from .helpers import make_rgb


class ResizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.image = make_rgb(200, 100)

    def test_width_only_keeps_ratio(self) -> None:
        result = resize_image(self.image, width=100)
        self.assertEqual(result.size, (100, 50))

    def test_height_only_keeps_ratio(self) -> None:
        result = resize_image(self.image, height=50)
        self.assertEqual(result.size, (100, 50))

    def test_both_dimensions(self) -> None:
        result = resize_image(self.image, width=300, height=300)
        self.assertEqual(result.size, (300, 300))

    def test_original_not_modified(self) -> None:
        resize_image(self.image, width=10)
        self.assertEqual(self.image.size, (200, 100))

    def test_no_dimensions(self) -> None:
        with self.assertRaises(ImageToolError):
            resize_image(self.image)

    def test_zero_or_negative(self) -> None:
        with self.assertRaises(ImageToolError):
            resize_image(self.image, width=0)
        with self.assertRaises(ImageToolError):
            resize_image(self.image, height=-5)

    def test_rounding_never_gives_zero(self) -> None:
        tall = Image.new("RGB", (2, 100))
        result = resize_image(tall, height=1)
        self.assertGreaterEqual(result.width, 1)
        self.assertEqual(result.height, 1)


class CropTests(unittest.TestCase):
    def setUp(self) -> None:
        self.image = make_rgb(100, 80)

    def test_crop_size(self) -> None:
        result = crop_image(self.image, 10, 20, 60, 70)
        self.assertEqual(result.size, (50, 50))

    def test_out_of_bounds(self) -> None:
        with self.assertRaises(ImageToolError):
            crop_image(self.image, 0, 0, 101, 80)
        with self.assertRaises(ImageToolError):
            crop_image(self.image, -1, 0, 10, 10)

    def test_reversed_bounds(self) -> None:
        with self.assertRaises(ImageToolError):
            crop_image(self.image, 50, 0, 10, 10)
        with self.assertRaises(ImageToolError):
            crop_image(self.image, 0, 50, 10, 10)

    def test_empty_region(self) -> None:
        with self.assertRaises(ImageToolError):
            crop_image(self.image, 10, 10, 10, 20)


class RotateTests(unittest.TestCase):
    def test_90_swaps_dimensions(self) -> None:
        result = rotate_image(make_rgb(100, 60), 90)
        self.assertEqual(result.size, (60, 100))

    def test_180_keeps_dimensions(self) -> None:
        result = rotate_image(make_rgb(100, 60), 180)
        self.assertEqual(result.size, (100, 60))

    def test_270_swaps_dimensions(self) -> None:
        result = rotate_image(make_rgb(100, 60), 270)
        self.assertEqual(result.size, (60, 100))

    def test_invalid_angle(self) -> None:
        with self.assertRaises(ImageToolError):
            rotate_image(make_rgb(), 45)

    def test_direction_is_clockwise(self) -> None:
        image = make_rgb(4, 2)  # 左上红、右上绿、左下蓝、右下黄
        result = rotate_image(image, 90)
        # 顺时针 90°：左上角应为原来的左下角（蓝）
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 255))


class FlipTests(unittest.TestCase):
    def test_horizontal(self) -> None:
        image = make_rgb(4, 2)
        result = flip_image(image, "horizontal")
        self.assertEqual(result.getpixel((3, 0)), (255, 0, 0))
        self.assertEqual(result.getpixel((0, 0)), (0, 255, 0))

    def test_vertical(self) -> None:
        image = make_rgb(4, 2)
        result = flip_image(image, "vertical")
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 255))

    def test_invalid_direction(self) -> None:
        with self.assertRaises(ImageToolError):
            flip_image(make_rgb(), "diagonal")


class GrayscaleTests(unittest.TestCase):
    def test_rgb_to_l(self) -> None:
        result = grayscale_image(make_rgb())
        self.assertEqual(result.mode, "L")

    def test_already_gray_returns_copy(self) -> None:
        gray = Image.new("L", (10, 10), 128)
        result = grayscale_image(gray)
        self.assertEqual(result.mode, "L")
        self.assertIsNot(result, gray)


if __name__ == "__main__":
    unittest.main()
