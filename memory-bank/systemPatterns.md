# System Patterns

## Architecture Status

Initial prototype scaffold is in place. The first implementation targets local image-based certificate classification using ELA preprocessing and a simple CNN, with a synthetic data generator for privacy-safe smoke testing.

## Preferred Design Principles

- Separate document ingestion, extraction, analysis, and result presentation.
- Keep detection rules testable as pure functions where practical.
- Distinguish deterministic checks from heuristic or model-assisted observations.
- Preserve traceability from each finding back to the source evidence.
- Make uncertain or unsupported checks explicit in the result model.

## Candidate Components

- Dataset storage: local `dataset/real` and `dataset/fake` folders. Real certificates should not be committed.
- Synthetic data: `generate_synthetic_dataset.py` creates balanced local starter images and `docs/synthetic_dataset_log.csv`.
- ELA preprocessing: `ela_converter.py` converts labeled images into `ela_images/real` and `ela_images/fake`.
- Model training: `train_model.py` trains a TensorFlow/Keras CNN with `real=0` and `fake=1`, then writes metrics, predictions, and a confusion matrix.
- Prediction: `predict.py` converts one uploaded image to ELA in memory, loads the trained model, and returns label plus confidence.
- Entry point: `main.py` exposes `sample-data`, `ela`, `train`, `predict`, and `web` subcommands.
- Optional UI: `app/web_app.py` provides a minimal Flask upload interface after dependencies and model are available.
- Future analysis layers: OCR, metadata checks, issuer validation, heatmaps, and explanation-oriented results remain future scope.

## Decision Log

- 2026-05-22: Initialized Memory Bank before application code was present.
- 2026-05-22: Adopted modular Memory Bank files following the Agentic Coding Handbook pattern.
- 2026-05-22: Chose a beginner-friendly local Python prototype with root-level scripts matching the requested folder structure.
- 2026-05-22: Adopted ELA preprocessing before model training so the CNN learns from tamper-sensitive image differences.
- 2026-05-22: Kept TensorFlow and Flask imports lazy so ELA utilities and tests can run before full ML dependencies are installed.
- 2026-05-22: Added a synthetic certificate dataset generator to avoid committing private certificate data while keeping the phase plan executable.
- 2026-05-22: Added explicit evaluation artifact outputs for reportability: metrics JSON, confusion matrix CSV, and validation prediction CSV.
- 2026-05-22: Switched Flask upload temporary handling to `TemporaryDirectory` paths for Windows compatibility.

## Open Architecture Questions

- Should the first demonstration use only the CLI, or include the optional Flask UI?
- Which certificate image formats should be accepted for final submission beyond JPG/PNG?
- Will later versions add OCR, forged signature/seal detection, or issuer verification?
- What privacy guarantees are required for uploaded certificates?
- Should synthetic data generation remain only a smoke-test fixture once real consented data is available?
