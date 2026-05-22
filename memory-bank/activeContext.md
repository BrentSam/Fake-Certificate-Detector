# Active Context

## Current Focus

Implement the phase plan for the "Fake Internship Certificate Detector Using ELA and CNN" prototype and verify the full local workflow on synthetic data.

## Recent Changes

- Created `AGENTS.md` with startup and update rules for coding agents.
- Created modular Memory Bank files under `memory-bank/`.
- Recorded that the workspace had no visible application code at initialization.
- Reviewed `C:\Users\xenog\Downloads\Initial Instructions for Project Work.docx`.
- Added project scaffold: `dataset/`, `ela_images/`, `model/`, `app/`, `docs/`, and `tests/`.
- Added ELA preprocessing in `ela_converter.py`.
- Added starter CNN training in `train_model.py`.
- Added single-image prediction in `predict.py`.
- Added CLI subcommands in `main.py`.
- Added optional Flask upload UI in `app/web_app.py` and `app/templates/index.html`.
- Added setup and planning docs in `README.md`, `docs/phase_plan.md`, `docs/literature_survey_template.md`, and `docs/project_log.md`.
- Added lightweight ELA tests in `tests/test_ela_converter.py`.
- Added `generate_synthetic_dataset.py` plus `main.py sample-data` for privacy-safe synthetic certificate generation.
- Added dataset ethics guidance in `docs/data_collection_guidelines.md`.
- Filled the literature survey with 7 reviewed sources and added `docs/report_outline.md`.
- Added training evaluation artifacts: JSON metrics, CSV confusion matrix, and CSV validation predictions.
- Added tests for synthetic data generation, training metric writers, and Flask upload handling.
- Installed TensorFlow, Flask, scikit-learn, OpenCV, and related dependencies in the Codex bundled Python runtime.
- Generated 50 synthetic real and 50 synthetic fake local images, then generated matching 50/50 ELA outputs.
- Trained a first synthetic-data CNN baseline and saved `model/certificate_cnn.keras`.
- Fixed the Flask upload route to use a temporary directory path on Windows.
- Verified CLI prediction and the Flask GET/upload workflow; saved `docs/screenshots/web_ui_home.png`.

## Working Assumptions

- The first version focuses on image inputs, not PDFs.
- ELA images are the CNN training input.
- Class mapping is `real=0` and `fake=1`.
- The optional Flask UI will be used only after dependencies are installed and a model is trained.
- Real certificates and model artifacts should remain local and uncommitted.
- Memory files should remain concise, factual, and updated as decisions are made.
- Synthetic validation scores are smoke-test results only and should not be presented as real-world accuracy.

## Open Questions

- Which data source will supply consented real certificates, and how will personal data be anonymized?
- Should the first review/demo use CLI only or the Flask UI?
- Should OpenCV-based heatmaps be added in the first prototype or kept for future scope?
- What level of data retention, if any, is acceptable?

## Next Steps

- Replace or supplement synthetic data with consented/anonymized real certificate images.
- Use `docs/training_metrics.json`, `docs/confusion_matrix.csv`, and `docs/validation_predictions.csv` in the report.
- Add screenshots of ELA outputs and prediction results for the final submission.
- Consider heatmaps, OCR, issuer checks, and PDF support as future phases.
