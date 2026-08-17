from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate_medical_certificates


class MedicalDatasetTests(unittest.TestCase):
    def test_generate_dataset_creates_files_and_logs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "dataset_medical"
            log_path = Path(temp_dir) / "docs" / "medical_synthetic_dataset_log.csv"

            summary = generate_medical_certificates.generate_dataset(
                count_per_class=2,
                output_root=output_root,
                log_path=log_path,
                seed=42,
                overwrite=True,
            )

            self.assertEqual(summary["real"], 2)
            self.assertEqual(summary["fake"], 2)

            real_files = list((output_root / "real").glob("*.jpg"))
            fake_files = list((output_root / "fake").glob("*.jpg"))

            self.assertEqual(len(real_files), 2)
            self.assertEqual(len(fake_files), 2)

            self.assertTrue(log_path.exists())
            with log_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            # 1 header + 4 image entries = 5 lines total
            self.assertEqual(len(lines), 5)


if __name__ == "__main__":
    unittest.main()
