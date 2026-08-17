# Fake Certificate Detector

A Python-based tool that detects fake **internship** and **medical** certificates using **Error Level Analysis (ELA)** and a **Convolutional Neural Network (CNN)** built on EfficientNetB0.

> **What it does:** This tool analyzes certificate images to flag potential visual tampering. It is a first-pass screening tool and cannot prove absolute authenticity without verification from the issuing organization.

---

## Table of Contents

- [What You Need](#what-you-need)
- [Quick Start](#quick-start)
- [Certificate Types](#certificate-types)
- [Project Structure](#project-structure)
- [Detailed Usage](#detailed-usage)
- [Web Interface](#web-interface)
- [Model Performance](#model-performance)
- [Running Tests](#running-tests)
- [Important Notes](#important-notes)

---

## What You Need

- **Python 3.13 or higher**
- **uv** (Python package and project manager)
- A terminal (PowerShell, Command Prompt, or any shell)

All dependencies are declared in `pyproject.toml` and will be installed automatically by `uv`.

---

## Quick Start

### Step 1: Install Dependencies

```powershell
uv sync
```

Then run any command with `uv run`:

```powershell
uv run python main.py --help
```

> On macOS/Linux, you can alternatively activate the environment with: `source .venv/bin/activate`.

### Step 2: Generate Synthetic Dataset

Generate privacy-safe synthetic certificates for training. Use `--cert-type` to choose between **internship** and **medical** certificates:

```powershell
# Generate 500 internship certificates (250 real + 250 fake)
uv run python main.py sample-data --cert-type internship --count 500

# Generate 500 medical certificates (250 real + 250 fake)
uv run python main.py sample-data --cert-type medical --count 500
```

Output directories:
- `dataset_internship/real/` and `dataset_internship/fake/`
- `dataset_medical/real/` and `dataset_medical/fake/`

**Want to use your own images?** Place certificate images into the appropriate `real/` and `fake/` subdirectories.

### Step 3: Convert to ELA Images

Transform the dataset into Error Level Analysis images. ELA highlights areas that may have been digitally altered:

```powershell
# Convert internship certificates
uv run python main.py ela --cert-type internship

# Convert medical certificates
uv run python main.py ela --cert-type medical
```

Output directories:
- `ela_images_internship/real/` and `ela_images_internship/fake/`
- `ela_images_medical/real/` and `ela_images_medical/fake/`

### Step 4: Train the Models

Train a separate CNN model for each certificate type:

```powershell
# Train internship model
uv run python main.py train --cert-type internship --epochs 25 --fine-tune-epochs 15

# Train medical model
uv run python main.py train --cert-type medical --epochs 25 --fine-tune-epochs 15
```

This saves:
- `model/internship_cnn.keras` and `model/medical_cnn.keras` — trained models
- `docs/<type>_training_metrics.json` — accuracy, precision, recall, F1-score
- `docs/<type>_confusion_matrix.csv` — performance breakdown
- `docs/<type>_validation_predictions.csv` — individual validation predictions

### Step 5: Predict (Detect Fake Certificates)

Classify a single certificate image:

```powershell
# Predict an internship certificate
uv run python main.py predict "path\to\certificate.jpg" --cert-type internship

# Predict a medical certificate
uv run python main.py predict "path\to\certificate.jpg" --cert-type medical
```

The output shows whether the certificate is predicted as **Real** or **Fake**, along with a confidence score.

---

## Certificate Types

The system supports two certificate types, each with its own dedicated model:

| Type | Dataset Directory | ELA Directory | Model File |
|------|------------------|---------------|------------|
| **Internship** | `dataset_internship/` | `ela_images_internship/` | `model/internship_cnn.keras` |
| **Medical** | `dataset_medical/` | `ela_images_medical/` | `model/medical_cnn.keras` |

Use `--cert-type internship` or `--cert-type medical` with any command to target the specific type.

---

## Project Structure

```text
Fake Certificate Detector/
├── app/                             # Web application
│   ├── templates/                   # HTML templates (login, signup, dashboard, etc.)
│   ├── auth.py                      # Authentication (login/signup with SQLite)
│   └── web_app.py                   # Flask app with blueprints
├── dataset_internship/              # Internship certificate images
│   ├── real/
│   └── fake/
├── dataset_medical/                 # Medical certificate images
│   ├── real/
│   └── fake/
├── ela_images_internship/           # Preprocessed ELA images (internship)
│   ├── real/
│   └── fake/
├── ela_images_medical/              # Preprocessed ELA images (medical)
│   ├── real/
│   └── fake/
├── model/                           # Trained model files
│   ├── internship_cnn.keras
│   └── medical_cnn.keras
├── demo_certificates/               # Demo certificates for presentation
├── docs/                            # Documentation, metrics, and logs
├── tests/                           # Unit tests
├── memory-bank/                     # Project working context
├── generate_synthetic_dataset.py    # Internship certificate generator
├── generate_medical_certificates.py # Medical certificate generator
├── ela_converter.py                 # ELA image converter
├── train_model.py                   # CNN model architecture and training
├── predict.py                       # Single image prediction
├── main.py                          # Main entry point (CLI)
├── run_demo_predictions.py          # Demo prediction script
├── pyproject.toml                   # Project dependencies and metadata
└── uv.lock                         # Lockfile created by uv
```

---

## Detailed Usage

### Web Interface

The project includes a full web application with authentication and drag-and-drop certificate validation:

```powershell
uv run app.py
```

Then open your browser to: **http://127.0.0.1:5000**

**Features:**
- User registration and login (SQLite-backed authentication)
- Certificate type selection (internship or medical)
- Drag-and-drop image upload
- Real-time ELA analysis and prediction display
- Confidence scores and result visualization

### Running Demo Predictions

To showcase the system's accuracy with sample certificates:

```powershell
# 1. Generate demo certificates
uv run python main.py sample-data --cert-type internship --count 5 --output demo_certificates/internship --overwrite
uv run python main.py sample-data --cert-type medical --count 5 --output demo_certificates/medical --overwrite

# 2. Run predictions and see the summary
uv run python run_demo_predictions.py
```

### Command Line Help

For help on any command, use `--help`:

```powershell
uv run python main.py --help
uv run python main.py sample-data --help
uv run python main.py train --help
uv run python main.py predict --help
```

---

## Model Performance

The CNN uses **EfficientNetB0** as a backbone with transfer learning. Training uses a two-phase approach:

1. **Phase 1**: Train the top classifier with the backbone frozen (25 epochs)
2. **Phase 2**: Fine-tune the last 30 backbone layers with a low learning rate (15 epochs)

**Architecture enhancements:**
- `RandomFlip`, `RandomRotation`, `RandomZoom`, `RandomTranslation`, `RandomBrightness`, `RandomContrast` data augmentation
- Dense(128) + BatchNormalization hidden layer
- Label smoothing (0.05) for regularization
- `ReduceLROnPlateau` learning rate scheduling

### Current Results (500 images per class)

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| **Internship** | **98.0%** | 100% | 96% | 0.98 |
| **Medical** | **98.5%** | 100% | 97% | 0.985 |

Both models achieve **zero false positives** — no real certificates are incorrectly flagged as fake.

---

## Running Tests

The project includes lightweight tests that do not require TensorFlow to run:

```powershell
uv run python -m unittest discover -s tests
```

These tests verify:
- ELA image generation works correctly
- Synthetic dataset generation produces valid output (both internship and medical)
- Training metrics are calculated properly
- Web app authentication and upload handling
- Flask routing and blueprints

---

## Important Notes

- **Privacy First:** Do not commit real certificates containing personal information to this repository. Use the synthetic dataset generator for testing, or carefully manage real data.
- **Detection, Not Proof:** This tool detects visual anomalies that may indicate tampering. A "Real" prediction does not guarantee authenticity, and a "Fake" prediction should be verified by the issuing organization.
- **Local Processing:** All image processing and model training happen locally on your machine. No data is sent to external servers.
- **Model Quality:** The accuracy of detection depends on the quality and quantity of your training dataset. More diverse real and fake examples will improve results.

---

## Troubleshooting

**Issue: `python` command not found**
- Solution: Make sure Python is installed and added to your system PATH.

**Issue: `pip install` fails**
- Solution: This project uses `uv`, not `pip`. Run `uv sync` to install dependencies.

**Issue: Training takes too long**
- Solution: Reduce epochs: `uv run python main.py train --cert-type internship --epochs 10`
- Or reduce batch size: `uv run python main.py train --cert-type internship --batch-size 4`

**Issue: Web UI does not open**
- Solution: Manually visit `http://127.0.0.1:5000` in your browser after running `uv run app.py`.

---

## Documentation

Additional project documents are available in the `docs/` folder:

- `docs/phase_plan.md` - Project implementation phases
- `docs/data_collection_guidelines.md` - How to collect data safely and legally
- `docs/literature_survey_template.md` - Research background
- `docs/report_outline.md` - Final report and presentation structure
- `docs/project_log.md` - Implementation and experiment log
