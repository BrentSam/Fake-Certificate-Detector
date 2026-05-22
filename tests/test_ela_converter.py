from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from ela_converter import convert_dataset, make_ela_image


class ElaConverterTests(unittest.TestCase):
    def test_make_ela_image_returns_requested_size(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "certificate.png"
            image = Image.new("RGB", (220, 140), "white")
            draw = ImageDraw.Draw(image)
            draw.rectangle((20, 20, 200, 120), outline="black", width=3)
            draw.text((40, 60), "Internship Certificate", fill="black")
            image.save(source)

            ela_image = make_ela_image(source, quality=90, size=128)

            self.assertEqual(ela_image.size, (128, 128))
            self.assertEqual(ela_image.mode, "RGB")

    def test_convert_dataset_writes_labeled_ela_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dataset = root / "dataset"
            output = root / "ela_images"
            (dataset / "real").mkdir(parents=True)
            (dataset / "fake").mkdir(parents=True)

            Image.new("RGB", (64, 64), "white").save(dataset / "real" / "real_one.png")
            Image.new("RGB", (64, 64), "gray").save(dataset / "fake" / "fake_one.png")

            counts = convert_dataset(dataset, output, size=64)

            self.assertEqual(counts, {"real": 1, "fake": 1})
            self.assertTrue((output / "real" / "real_one.jpg").exists())
            self.assertTrue((output / "fake" / "fake_one.jpg").exists())


if __name__ == "__main__":
    unittest.main()
