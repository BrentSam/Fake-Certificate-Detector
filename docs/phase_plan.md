# Phase Plan

This plan follows the initial instruction document: understand the problem,
focus on data, survey related work, implement in phases, evaluate clearly, and
document the process.

## Phase 0: Project Setup

Goal: Prepare a clean project structure for a working prototype.

Deliverables:

- Memory Bank and project scaffold.
- Dataset, ELA output, model, app, docs, and tests folders.
- Starter scripts for ELA conversion, CNN training, prediction, and optional web UI.
- `requirements.txt`, `.gitignore`, and README setup instructions.

Status: Completed scaffold. Dependencies are installed in the verified runtime. A
privacy-safe synthetic starter dataset can be generated with `python main.py
sample-data --count 50`.

## Phase 1: Data Collection And Ethics

Goal: Build a small custom dataset.

Tasks:

- Collect 50-100 real internship certificate images.
- Create 50-100 fake or edited versions by changing names, dates, seals, signatures, or text.
- Keep personal data private. Prefer consented, anonymized, or synthetic certificates.
- Maintain a simple dataset log with source type, class label, and edit type.

Success checks:

- `dataset/real` and `dataset/fake` contain balanced image counts.
- No private certificates are committed to version control.

Status: Implemented with synthetic local data. Generated 50 real and 50 fake
synthetic certificate images plus `docs/synthetic_dataset_log.csv`. Consented
real certificate collection remains future work.

## Phase 2: Literature Survey

Goal: Review credible prior work before model development.

Tasks:

- Read 5-8 papers or credible technical sources.
- Focus on ELA, image forgery detection, CNN-based tamper classification, and document fraud detection.
- Record methods, strengths, limitations, and research gaps.

Success checks:

- `docs/literature_survey_template.md` is filled with at least 5 reviewed works.
- The chosen ELA plus CNN approach is justified.

Status: Completed with 7 reviewed works and a research gap summary.

## Phase 3: ELA Preprocessing

Goal: Convert original certificate images into ELA images.

Tasks:

- Resize inputs to 128x128.
- Recompress images with JPEG quality 90.
- Store processed images in `ela_images/real` and `ela_images/fake`.

Command:

```powershell
python ela_converter.py --input dataset --output ela_images --size 128
```

Success checks:

- ELA image count matches the dataset image count.
- A few outputs are visually inspected for obvious conversion issues.

Status: Completed on synthetic data. Generated 50 real and 50 fake ELA images.

## Phase 4: CNN Model Development

Goal: Train a simple binary classifier.

Tasks:

- Use Conv2D, MaxPooling2D, Flatten, Dense, Dropout, and sigmoid output layers.
- Use `real=0` and `fake=1`.
- Split data into training and validation sets.

Command:

```powershell
python train_model.py --data ela_images --epochs 10
```

Success checks:

- Model saves to `model/certificate_cnn.keras`.
- Training and validation metrics are recorded.

Status: Completed on synthetic ELA data. Model saved to
`model/certificate_cnn.keras`.

## Phase 5: Evaluation And Interpretation

Goal: Evaluate the model beyond accuracy.

Tasks:

- Report accuracy, precision, recall, F1-score, and confusion matrix.
- Compare correct and incorrect predictions.
- Explain where the model is uncertain or weak.

Success checks:

- Results are documented in the project report/logbook.
- Limitations are clearly stated.

Status: Completed for the synthetic baseline. Metrics are saved to
`docs/training_metrics.json`, `docs/confusion_matrix.csv`, and
`docs/validation_predictions.csv`. The result is documented as a smoke test, not
real-world accuracy.

## Phase 6: Prediction Workflow

Goal: Classify a newly uploaded certificate image.

Tasks:

- Convert the uploaded image to ELA format in memory.
- Load the trained CNN model.
- Output Real Certificate or Fake Certificate with confidence.

Command:

```powershell
python predict.py "path\to\certificate.jpg"
```

Success checks:

- Prediction works on held-out images.
- Output includes label, confidence, and fake probability.

Status: Completed for local synthetic samples using `python main.py predict`.

## Phase 7: Optional Web UI

Goal: Provide a simple upload interface.

Tasks:

- Run Flask app.
- Upload certificate image.
- Display predicted class and confidence.

Command:

```powershell
python main.py web
```

Success checks:

- Web UI opens locally.
- Upload flow works after a model has been trained.

Status: Completed. Flask GET and upload route passed local smoke tests, and
`docs/screenshots/web_ui_home.png` was captured.

## Phase 8: Report And Presentation

Goal: Prepare academic submission materials.

Tasks:

- Include problem statement, objectives, workflow, dataset details, model architecture, metrics, screenshots, and future scope.
- Add citations from the literature survey.
- Include screenshots of ELA images, training output, confusion matrix, and prediction UI.

Success checks:

- The final report answers: what problem was solved, how it was solved, and how effective it was.

Status: Partially implemented. `docs/report_outline.md` is ready; final report
writing and additional screenshots remain pending.
