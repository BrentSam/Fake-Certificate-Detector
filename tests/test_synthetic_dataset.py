from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from generate_synthetic_dataset import generate_dataset


class SyntheticDatasetTests(unittest.TestCase):
    def test_generate_dataset_writes_balanced_images_and_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "dataset"
            log_path = root / "docs" / "synthetic_dataset_log.csv"

            summary = generate_dataset(count_per_class=3, output_root=output, log_path=log_path, seed=7)

            self.assertEqual(summary["real"], 3)
            self.assertEqual(summary["fake"], 3)
            self.assertEqual(len(list((output / "real").glob("synthetic_real_*.jpg"))), 3)
            self.assertEqual(len(list((output / "fake").glob("synthetic_fake_*.jpg"))), 3)
            self.assertTrue(log_path.exists())

            with log_path.open(newline="", encoding="utf-8") as log_file:
                rows = list(csv.DictReader(log_file))

            self.assertEqual(len(rows), 6)
            self.assertEqual({row["class_label"] for row in rows}, {"real", "fake"})
            self.assertIn("edit_type", rows[0])

    def test_generate_dataset_protects_existing_synthetic_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dataset"
            log_path = Path(temp_dir) / "docs" / "synthetic_dataset_log.csv"

            generate_dataset(count_per_class=1, output_root=output, log_path=log_path, seed=1)

            with self.assertRaises(FileExistsError):
                generate_dataset(count_per_class=1, output_root=output, log_path=log_path, seed=1)


if __name__ == "__main__":
    unittest.main()
