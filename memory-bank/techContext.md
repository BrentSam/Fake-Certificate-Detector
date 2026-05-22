# Tech Context

## Current Stack

- Python local prototype.
- Pillow for ELA preprocessing.
- NumPy for image array preparation.
- TensorFlow/Keras for CNN training and prediction.
- Scikit-learn for precision, recall, F1-score, and confusion matrix output.
- Flask for the optional upload UI.
- `unittest` for lightweight tests that do not require TensorFlow.

## Workspace Notes

- Workspace path: `C:\Users\xenog\OneDrive\Documents\Fake Certificate Detector`
- Initial scaffold now includes `dataset/`, `ela_images/`, `model/`, `app/`, `docs/`, `tests/`, and root scripts.
- Local datasets and trained model artifacts are ignored by `.gitignore` to avoid committing sensitive or large files.
- Dependencies were installed into the Codex bundled Python runtime on 2026-05-22 for verification.
- `python` and `git` were not available on PATH in the shell; verification used the Codex bundled Python executable.
- `Start-Process` failed in PowerShell because of duplicate `Path`/`PATH` environment keys; web UI verification used the in-app browser runtime to launch Flask.

## Setup Commands

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py sample-data --count 50
python ela_converter.py --input dataset --output ela_images --size 128
python train_model.py --data ela_images --epochs 10
python predict.py "path\to\certificate.jpg"
```

## Tooling Still To Decide

- OCR and document parsing approach for future text verification.
- Whether OpenCV is needed in the first prototype beyond being available for future image operations.
- Packaging or deployment target, if any.

## Technical Constraints

- Certificates may contain sensitive personal data. Prefer local processing or clearly documented data handling.
- Do not commit real personal certificates as test fixtures.
- Detection results should preserve uncertainty and avoid unsupported authenticity claims.
- If external APIs are introduced, document their purpose, data sent, privacy implications, and failure behavior here.

## Suggested Initial Verification

Initial verification added:

- `tests/test_ela_converter.py` checks ELA image generation and labeled dataset conversion.
- `tests/test_synthetic_dataset.py` checks synthetic dataset generation and log writing.
- `tests/test_training_metrics.py` checks binary metric calculations and artifact writers.
- `tests/test_web_app.py` checks Flask upload handling without requiring TensorFlow prediction.

Verified locally on 2026-05-22:

- `python -m unittest discover -s tests` passed with 7 tests.
- `python -m py_compile generate_synthetic_dataset.py ela_converter.py train_model.py predict.py main.py app/web_app.py` passed.
- `python main.py sample-data --count 50` generated 50 real and 50 fake synthetic images.
- `python main.py ela --input dataset --output ela_images --size 128` generated 50 real and 50 fake ELA images.
- `python main.py train --data ela_images --epochs 10 --batch-size 8` saved the model and evaluation artifacts.
- `python main.py predict` worked on one synthetic fake and one synthetic real image.
- Flask GET and upload workflow passed local smoke tests.

Future tests should cover:

- Accepted and rejected file types.
- Empty, corrupt, or unreadable uploads.
- OCR or extraction failure behavior.
- Known suspicious certificate examples using synthetic fixtures.
- Result formatting and risk-level boundaries.
