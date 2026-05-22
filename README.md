# Fake Internship Certificate Detector

A beginner-friendly Python prototype that detects fake internship certificates using **Error Level Analysis (ELA)** and a **Convolutional Neural Network (CNN)**.

> **What it does:** This tool analyzes certificate images to flag potential visual tampering. It is a first-pass screening tool and cannot prove absolute authenticity without verification from the issuing organization.

---

## Table of Contents

- [What You Need](#what-you-need)
- [Quick Start (5 Steps)](#quick-start-5-steps)
- [Project Structure](#project-structure)
- [Detailed Usage](#detailed-usage)
- [Running Tests](#running-tests)
- [Important Notes](#important-notes)

---

## What You Need

- **Python 3.8 or higher**
- **pip** (Python package installer)
- A terminal (PowerShell, Command Prompt, or any shell)

All dependencies are listed in `requirements.txt` and will be installed automatically.

---

## Quick Start (5 Steps)

Follow these commands in order to get the detector running.

### Step 1: Install Dependencies

Create a virtual environment and install required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

> On macOS/Linux, use: `source .venv/bin/activate` instead of `.\.venv\Scripts\activate`.

### Step 2: Prepare Dataset Images

Generate a privacy-safe synthetic starter dataset to test the pipeline:

```powershell
python main.py sample-data --count 50
```

This creates:
- `dataset/real/` - 50 synthetic real certificate images
- `dataset/fake/` - 50 synthetic fake certificate images
- `docs/synthetic_dataset_log.csv` - a log of generated data

**Want to use your own images?** Simply place your certificate images into:
- `dataset/real/` for genuine certificates
- `dataset/fake/` for known fake/forged certificates

### Step 3: Convert to ELA Images

Transform the dataset into Error Level Analysis (ELA) images. ELA highlights areas of an image that may have been digitally altered:

```powershell
python main.py ela --input dataset --output ela_images --size 128
```

This creates:
- `ela_images/real/` - ELA versions of real certificates
- `ela_images/fake/` - ELA versions of fake certificates

### Step 4: Train the Model

Train the CNN on the ELA images:

```powershell
python main.py train --data ela_images --epochs 10
```

This saves several files:
- `model/certificate_cnn.keras` - the trained neural network model
- `docs/training_metrics.json` - accuracy, precision, recall, and F1-score
- `docs/confusion_matrix.csv` - model performance breakdown
- `docs/validation_predictions.csv` - predictions on validation data

### Step 5: Predict (Detect Fake Certificates)

Classify a single certificate image:

```powershell
python main.py predict "path\to\certificate.jpg"
```

The script will output whether the certificate is predicted as **Real** or **Fake**, along with a confidence score.

---

## Project Structure

```text
Fake Certificate Detector/
|-- dataset/                    # Your certificate images
|   |-- real/
|   `-- fake/
|-- ela_images/                 # Preprocessed ELA images
|   |-- real/
|   `-- fake/
|-- model/                      # Trained model files
|-- app/                        # Web application
|   |-- templates/
|   `-- web_app.py
|-- docs/                       # Documentation and logs
|-- tests/                      # Unit tests
|-- generate_synthetic_dataset.py
|-- ela_converter.py
|-- train_model.py
|-- predict.py
|-- main.py                     # Main entry point (CLI)
`-- requirements.txt
```

---

## Detailed Usage

### Using the Web Interface

For a drag-and-drop upload interface, run the Flask web server:

```powershell
python main.py web
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

Upload a certificate image, and the web UI will show the prediction result.

### Running Individual Scripts

Instead of using `main.py`, you can run each step directly:

**Generate synthetic data:**
```powershell
python generate_synthetic_dataset.py --count 50
```

**Convert to ELA:**
```powershell
python ela_converter.py --input dataset --output ela_images --size 128
```

**Train model:**
```powershell
python train_model.py --data ela_images --epochs 10
```

**Predict:**
```powershell
python predict.py "path\to\certificate.jpg"
```

### Command Line Help

For help on any command, use `--help`:

```powershell
python main.py --help
python main.py train --help
python main.py predict --help
```

---

## Running Tests

The project includes lightweight tests that do not require TensorFlow to run:

```powershell
python -m unittest discover -s tests
```

These tests verify:
- ELA image generation works correctly
- Synthetic dataset generation produces valid output
- Training metrics are calculated properly
- Web app upload handling functions correctly

---

## Important Notes

- **Privacy First:** Do not commit real certificates containing personal information to this repository. Use the synthetic dataset generator for testing, or carefully manage real data.
- **Detection, Not Proof:** This tool detects visual anomalies that may indicate tampering. A "Real" prediction does not guarantee authenticity, and a "Fake" prediction should be verified by the issuing organization.
- **Local Processing:** All image processing and model training happen locally on your machine. No data is sent to external servers.
- **Model Quality:** The accuracy of detection depends on the quality and quantity of your training dataset. More diverse real and fake examples will improve results.

---

## Documentation

Additional project documents are available in the `docs/` folder:

- `docs/phase_plan.md` - Project implementation phases
- `docs/data_collection_guidelines.md` - How to collect data safely and legally
- `docs/literature_survey_template.md` - Research background
- `docs/report_outline.md` - Final report and presentation structure
- `docs/project_log.md` - Implementation and experiment log

---

## Troubleshooting

**Issue: `python` command not found**
- Solution: Make sure Python is installed and added to your system PATH.

**Issue: `pip install` fails**
- Solution: Make sure your virtual environment is activated (you should see `(.venv)` in your terminal prompt).

**Issue: Training takes too long**
- Solution: Reduce the number of epochs: `python main.py train --data ela_images --epochs 5`
- Or reduce batch size if you run out of memory: `python main.py train --data ela_images --epochs 10 --batch-size 4`

**Issue: Web UI does not open**
- Solution: Manually visit `http://127.0.0.1:5000` in your browser after running `python main.py web`.
