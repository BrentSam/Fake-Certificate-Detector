# Report Outline

Use this outline for the final academic report and presentation.

## 1. Problem Statement

Explain why fake internship certificates are difficult to review manually and
why automated screening can help reviewers prioritize suspicious documents.

## 2. Objectives

- Build a local image-based fake certificate screening prototype.
- Convert certificate images to ELA images.
- Train a CNN classifier with `real=0` and `fake=1`.
- Report accuracy, precision, recall, F1-score, and confusion matrix.
- Present predictions as screening results, not legal proof.

## 3. Literature Survey

Summarize the works in `docs/literature_survey_template.md`, focusing on:

- ELA and JPEG artifact analysis.
- CNN-based manipulation detection.
- Document tampering detection.
- Limits of general image-forensics methods on certificate images.

## 4. Dataset

Document:

- Number of real and fake samples.
- Source type and anonymization process.
- Fake edit categories.
- Dataset balance.
- Privacy precautions.

Reference `docs/synthetic_dataset_log.csv` for the synthetic baseline or a local
ignored dataset log for real data.

## 5. Methodology

Include the pipeline:

```text
certificate image -> ELA conversion -> CNN training -> validation metrics -> prediction output
```

Mention the main files:

- `generate_synthetic_dataset.py`
- `ela_converter.py`
- `train_model.py`
- `predict.py`
- `app/web_app.py`

## 6. Model Architecture

Describe the CNN layers used in `train_model.py`:

- Rescaling.
- Conv2D and MaxPooling2D blocks.
- Flatten.
- Dense layer.
- Dropout.
- Sigmoid output.

## 7. Results

Use generated outputs after training:

- `docs/training_metrics.json`
- `docs/confusion_matrix.csv`
- `docs/validation_predictions.csv`

Compare correct and incorrect predictions. Note uncertain examples near the
0.5 fake-probability threshold.

## 8. Screenshots

Capture:

- Sample certificate images.
- ELA outputs.
- Training terminal output.
- Confusion matrix or metrics table.
- CLI prediction result.
- Optional Flask upload UI result.

## 9. Limitations

- ELA depends on compression history.
- Synthetic certificates do not fully represent real-world certificate variety.
- A small CNN can overfit small datasets.
- The model does not verify issuers or certificate IDs.
- The result is a first-pass screening signal.

## 10. Future Scope

- OCR extraction of names, dates, IDs, and issuer fields.
- Issuer verification workflow.
- Heatmap or tampered-region localization.
- PDF input support.
- Larger consented dataset and cross-domain testing.
