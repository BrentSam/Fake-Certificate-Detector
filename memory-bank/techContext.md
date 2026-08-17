# Tech Context

## Tech Stack

- **Python**: Core scripting and neural networks.
- **Flask**: Web application server framework.
- **Flask-Login**: Session management and route protection.
- **SQLite**: Local relational database for user accounts.
- **TensorFlow/Keras**: Convolutional Neural Networks training & loading using `EfficientNetB0` transfer learning.
- **Pillow**: Image processing and ELA conversions.
- **scikit-learn**: Validation reporting and confusion matrix calculations.
- **unittest**: Test runners and mocking.

## Project Directory Structure

```
Fake Certificate Detector/
├── app/
│   ├── templates/
│   │   ├── base.html              Shared layout & styling
│   │   ├── login.html             Auth card
│   │   ├── signup.html            Registration card
│   │   ├── dashboard.html         Model selector
│   │   ├── validate.html          Upload form & result bars
│   │   └── index.html             Redirect page
│   ├── auth.py                    SQLite user operations
│   └── web_app.py                 Flask application factory
├── dataset_internship/            Source internship certificates
├── dataset_medical/               Source medical certificates
├── ela_images_internship/         Internship preprocessed images
├── ela_images_medical/            Medical preprocessed images
├── model/
│   ├── internship_cnn.keras       Internship classifier
│   └── medical_cnn.keras          Medical classifier
├── instance/
│   └── users.db                   SQLite database
├── generate_synthetic_dataset.py  Internship generator
├── generate_medical_certificates.py Medical generator
├── ela_converter.py               ELA preprocessor
├── train_model.py                 Training pipeline
├── predict.py                     Prediction pipeline
├── main.py                        CLI interface
└── tests/                         Testing suite
```

## Setup & Running Commands

```powershell
# Sync project packages
uv sync

# Generate datasets
uv run python main.py sample-data --cert-type internship --count 100
uv run python main.py sample-medical-data --count 100

# Convert to ELA
uv run python main.py ela --cert-type internship
uv run python main.py ela --cert-type medical

# Train both models
uv run python main.py train --cert-type internship --epochs 10 --fine-tune-epochs 5
uv run python main.py train --cert-type medical --epochs 10 --fine-tune-epochs 5

# Predict on image
uv run python main.py predict dataset_internship/real/internship_real_0001.jpg --cert-type internship

# Launch web server
uv run app.py
```

## Verification Logs

- **Auth & Route Tests**: Verified 10 unit tests successfully passed (`python -m unittest discover -s tests`).
- **Pipeline Integration**: Dataset generation, ELA conversion, training, and prediction flows successfully tested end-to-end for both certificate types.
