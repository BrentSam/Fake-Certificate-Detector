# Project Log

Use this as a diary/logbook for reviews.

## 2026-05-22

- Project scaffold created.
- Initial instruction document reviewed.
- Phase plan added in `docs/phase_plan.md`.
- Starter scripts added for ELA conversion, CNN training, prediction, and optional Flask UI.
- Added `generate_synthetic_dataset.py` and `main.py sample-data` for privacy-safe starter data.
- Added `docs/data_collection_guidelines.md` and `docs/report_outline.md`.
- Filled `docs/literature_survey_template.md` with 7 reviewed sources.
- Generated 50 synthetic real and 50 synthetic fake certificate images locally.
- Generated 50 real and 50 fake ELA images locally.
- Installed project dependencies into the Codex bundled Python runtime.
- Trained a first CNN baseline for 10 epochs on synthetic ELA data.
- Saved `model/certificate_cnn.keras`, `docs/training_metrics.json`, `docs/confusion_matrix.csv`, and `docs/validation_predictions.csv`.
- Validation on the synthetic split reported accuracy, precision, recall, and F1-score of 1.0 with confusion matrix `real: 8/8`, `fake: 12/12`.
- Verified CLI prediction on `dataset/fake/synthetic_fake_0001.jpg` and `dataset/real/synthetic_real_0001.jpg`.
- Fixed the Flask upload route for Windows temporary-file behavior and verified GET plus upload smoke tests.
- Captured `docs/screenshots/web_ui_home.png`.

## Next Entry

- Replace or supplement synthetic data with consented/anonymized real certificate examples before claiming real-world performance.
- Add report screenshots of ELA outputs and prediction results.
