# Progress

## Completed

- 2026-05-22: Initialized `AGENTS.md`.
- 2026-05-22: Initialized Memory Bank folder and core files:
  - `projectbrief.md`
  - `productContext.md`
  - `systemPatterns.md`
  - `techContext.md`
  - `activeContext.md`
  - `progress.md`
- 2026-05-22: Reviewed the initial instruction document from `C:\Users\xenog\Downloads\Initial Instructions for Project Work.docx`.
- 2026-05-22: Created prototype folder structure matching the project brief:
  - `dataset/real`, `dataset/fake`
  - `ela_images/real`, `ela_images/fake`
  - `model`
  - `app`
  - `docs`
  - `tests`
- 2026-05-22: Added `ela_converter.py`, `train_model.py`, `predict.py`, and `main.py`.
- 2026-05-22: Added optional Flask upload UI in `app/web_app.py`.
- 2026-05-22: Added `README.md`, `requirements.txt`, `.gitignore`, `docs/phase_plan.md`, `docs/literature_survey_template.md`, and `docs/project_log.md`.
- 2026-05-22: Added `tests/test_ela_converter.py` for ELA conversion.
- 2026-05-22: Verified ELA tests and Python syntax with bundled Python.
- 2026-05-22: Added `generate_synthetic_dataset.py` and `main.py sample-data`.
- 2026-05-22: Added `docs/data_collection_guidelines.md` and `docs/report_outline.md`.
- 2026-05-22: Filled `docs/literature_survey_template.md` with 7 reviewed works and a research gap summary.
- 2026-05-22: Added evaluation output writing in `train_model.py` for `docs/training_metrics.json`, `docs/confusion_matrix.csv`, and `docs/validation_predictions.csv`.
- 2026-05-22: Added tests for synthetic dataset generation, metric calculations/writers, and Flask upload handling.
- 2026-05-22: Generated a local synthetic dataset with 50 real and 50 fake images.
- 2026-05-22: Generated matching local ELA images with 50 real and 50 fake outputs.
- 2026-05-22: Installed project dependencies into the Codex bundled Python runtime.
- 2026-05-22: Trained the first CNN baseline on synthetic ELA images and saved `model/certificate_cnn.keras`.
- 2026-05-22: Recorded first synthetic validation metrics: accuracy 1.0, precision 1.0, recall 1.0, F1-score 1.0, confusion matrix TN=8, FP=0, FN=0, TP=12.
- 2026-05-22: Verified CLI predictions for one synthetic fake image and one synthetic real image.
- 2026-05-22: Fixed Windows upload handling in `app/web_app.py`.
- 2026-05-22: Verified Flask GET and upload flow locally and saved `docs/screenshots/web_ui_home.png`.

## In Progress

- Report and presentation evidence gathering.
- Real or consented dataset collection beyond synthetic smoke-test data.

## Pending

- Collect 50-100 real and 50-100 fake/edited certificate images locally, if available and consented.
- Re-run ELA conversion and training on the real/anonymized dataset.
- Compare correct and incorrect predictions on non-synthetic held-out images.
- Capture screenshots of ELA outputs, prediction output, and confusion matrix for report and presentation.
- Decide whether to include optional heatmap visualization.

## Blockers

- No consented real certificate dataset is present yet, so current metrics only validate the synthetic workflow.
