from __future__ import annotations

import tempfile
from pathlib import Path

from ela_converter import SUPPORTED_EXTENSIONS
from predict import predict_certificate


try:
    from flask import Flask, render_template, request
except ImportError:
    Flask = None
    render_template = None
    request = None


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def create_app(model_path: str | Path = "model/certificate_cnn.keras"):
    if Flask is None:
        raise SystemExit("Flask is required for the web UI. Install dependencies with: pip install -r requirements.txt")

    app = Flask(__name__)
    app.config["MODEL_PATH"] = str(model_path)

    @app.get("/")
    def index():
        return render_template("index.html", result=None, error=None)

    @app.post("/")
    def upload():
        upload_file = request.files.get("certificate")
        if upload_file is None or upload_file.filename == "":
            return render_template("index.html", result=None, error="Choose a certificate image first.")

        if not allowed_file(upload_file.filename):
            return render_template("index.html", result=None, error="Upload a JPG, PNG, BMP, TIFF, or WEBP image.")

        suffix = Path(upload_file.filename).suffix.lower()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / f"certificate_upload{suffix}"
            upload_file.save(temp_path)
            try:
                result = predict_certificate(temp_path, model_path=app.config["MODEL_PATH"])
            except SystemExit as exc:
                return render_template("index.html", result=None, error=str(exc))
            except Exception:
                return render_template(
                    "index.html",
                    result=None,
                    error="The image could not be analyzed. Check that the file is readable and try again.",
                )

        return render_template("index.html", result=result, error=None)

    return app
