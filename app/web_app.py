from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from ela_converter import SUPPORTED_EXTENSIONS
from predict import predict_certificate
from app.auth import init_db, create_user, authenticate_user, get_user_by_id


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def _count_files(directory: str | Path) -> int:
    path = Path(directory)
    if not path.exists():
        return 0
    try:
        return sum(1 for _ in path.rglob("*") if _.is_file())
    except OSError:
        return 0


def _model_info(model_path: str | Path) -> dict:
    path = Path(model_path)
    if not path.exists():
        return {"present": False, "size_mb": 0.0, "modified": None, "modified_label": "Not trained"}
    stat = path.stat()
    size_mb = round(stat.st_size / (1024 * 1024), 1)
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    delta = datetime.now(timezone.utc) - modified
    days = delta.days
    if days <= 0:
        hours = max(delta.seconds // 3600, 0)
        modified_label = f"Trained {hours}h ago" if hours else "Trained just now"
    elif days == 1:
        modified_label = "Trained 1 day ago"
    elif days < 30:
        modified_label = f"Trained {days} days ago"
    else:
        modified_label = modified.strftime("Trained %d %b %Y")
    return {
        "present": True,
        "size_mb": size_mb,
        "modified": modified.isoformat(),
        "modified_label": modified_label,
    }


def gather_system_stats(model_paths: dict[str, str | Path]) -> dict:
    """Compute honest, real-time statistics for the dashboard."""
    internship_model = _model_info(model_paths.get("internship", ""))
    medical_model = _model_info(model_paths.get("medical", ""))
    ela_internship = _count_files("ela_images_internship")
    ela_medical = _count_files("ela_images_medical")
    return {
        "ela_internship": ela_internship,
        "ela_medical": ela_medical,
        "ela_total": ela_internship + ela_medical,
        "internship_model": internship_model,
        "medical_model": medical_model,
        "active_models": sum(1 for m in (internship_model, medical_model) if m["present"]),
    }


def create_app(model_paths: dict[str, str | Path] | None = None, db_path: str | Path | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = "certiguard-secure-secret-key-1337"

    # Setup database path
    if db_path is None:
        db_dir = Path(app.instance_path)
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "users.db"
    app.config["DATABASE_PATH"] = str(db_path)
    
    # Initialize DB
    init_db(str(db_path))

    # Setup model paths
    if model_paths is None:
        model_paths = {
            "internship": "model/internship_cnn.keras",
            "medical": "model/medical_cnn.keras"
        }
    app.config["MODEL_PATHS"] = {k: str(v) for k, v in model_paths.items()}

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(app.config["DATABASE_PATH"], user_id)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
            
        if request.method == "POST":
            username_or_email = request.form.get("username_or_email")
            password = request.form.get("password")
            
            if not username_or_email or not password:
                flash("Please fill in all fields.", "error")
            else:
                user = authenticate_user(app.config["DATABASE_PATH"], username_or_email, password)
                if user:
                    login_user(user)
                    flash("Signed in successfully!", "success")
                    return redirect(url_for("dashboard"))
                else:
                    flash("Invalid username, email, or password.", "error")
                
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
            
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            
            if not username or not email or not password:
                flash("Please fill in all fields.", "error")
            else:
                user = create_user(app.config["DATABASE_PATH"], username, email, password)
                if user:
                    flash("Account created successfully! Please sign in.", "success")
                    return redirect(url_for("login"))
                else:
                    flash("Username or email already exists.", "error")
                
        return render_template("signup.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Signed out successfully.", "success")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        stats = gather_system_stats(app.config["MODEL_PATHS"])
        return render_template("dashboard.html", stats=stats)

    @app.route("/validate/<cert_type>", methods=["GET", "POST"])
    @login_required
    def validate(cert_type: str):
        if cert_type not in ["internship", "medical"]:
            flash("Invalid certificate type selected.", "error")
            return redirect(url_for("dashboard"))
            
        result = None
        error = None
        
        if request.method == "POST":
            upload_file = request.files.get("certificate")
            if upload_file is None or upload_file.filename == "":
                error = "Choose a certificate image first."
            elif not allowed_file(upload_file.filename):
                error = "Upload a JPG, PNG, BMP, TIFF, or WEBP image."
            else:
                suffix = Path(upload_file.filename).suffix.lower()
                model_path = app.config["MODEL_PATHS"].get(cert_type)
                
                import base64
                from io import BytesIO
                from ela_converter import make_ela_image

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / f"certificate_upload{suffix}"
                    file_content = upload_file.read()
                    temp_path.write_bytes(file_content)
                    
                    try:
                        result = predict_certificate(temp_path, model_path=model_path, cert_type=cert_type)
                        
                        if not result.get("valid", True):
                            error = "Invalid Format: The uploaded image does not appear to be a certificate."
                            result = None
                        else:
                            # Generate base64 Data URLs for original and ELA images
                            mime_type = "image/jpeg"
                            if suffix == ".png":
                                mime_type = "image/png"
                            elif suffix == ".webp":
                                mime_type = "image/webp"
                            elif suffix == ".gif":
                                mime_type = "image/gif"
                            
                            original_b64 = base64.b64encode(file_content).decode("utf-8")
                            result["original_image_url"] = f"data:{mime_type};base64,{original_b64}"
                            
                            # Generate ELA at original resolution
                            ela_image = make_ela_image(temp_path, quality=90, size=None)
                            ela_io = BytesIO()
                            ela_image.save(ela_io, format="JPEG")
                            ela_b64 = base64.b64encode(ela_io.getvalue()).decode("utf-8")
                            result["ela_image_url"] = f"data:image/jpeg;base64,{ela_b64}"
                        
                    except SystemExit as exc:
                        error = str(exc)
                    except Exception as e:
                        error = f"The image could not be analyzed. Check that the model exists and the file is readable."
                        
        return render_template("validate.html", cert_type=cert_type, result=result, error=error)

    return app
