from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from train_model import (
    calculate_binary_metrics,
    write_confusion_matrix_csv,
    write_metrics_json,
    write_validation_predictions_csv,
)


class TrainingMetricsTests(unittest.TestCase):
    def test_calculate_binary_metrics_reports_expected_values(self):
        metrics = calculate_binary_metrics([0, 0, 1, 1], [0.1, 0.8, 0.7, 0.2], threshold=0.5)

        self.assertEqual(metrics["samples"], 4)
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertEqual(metrics["precision"], 0.5)
        self.assertEqual(metrics["recall"], 0.5)
        self.assertEqual(metrics["f1_score"], 0.5)
        self.assertEqual(
            metrics["confusion_matrix"],
            {
                "true_negative": 1,
                "false_positive": 1,
                "false_negative": 1,
                "true_positive": 1,
            },
        )

    def test_metric_writers_create_report_files(self):
        metrics = calculate_binary_metrics([0, 1], [0.2, 0.9], threshold=0.5)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metrics_path = root / "metrics.json"
            confusion_path = root / "confusion.csv"
            predictions_path = root / "predictions.csv"

            write_metrics_json(metrics, metrics_path)
            write_confusion_matrix_csv(metrics, confusion_path)
            write_validation_predictions_csv(
                [0, 1],
                [0.2, 0.9],
                predictions_path,
                validation_paths=["real.jpg", "fake.jpg"],
            )

            self.assertTrue(metrics_path.exists())
            self.assertIn('"accuracy": 1.0', metrics_path.read_text(encoding="utf-8"))
            self.assertIn("actual\\predicted,real,fake", confusion_path.read_text(encoding="utf-8"))
            self.assertIn("real.jpg,real,real,0.200000,true", predictions_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
