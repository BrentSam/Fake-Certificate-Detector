# System Patterns

## Architecture Status

The multi-model system is fully implemented and verified. The single-model prototype has been expanded to support specialized models for internship and medical certificate types, SQLite authentication, and an interactive dashboard.

### Final Architecture
- **Two Specialized Models**: [internship_cnn.keras](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/model/internship_cnn.keras) and [medical_cnn.keras](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/model/medical_cnn.keras) trained on domain-specific ELA images.
- **Session Authentication**: Flask-Login backed by local SQLite DB at `instance/users.db`.
- **Dynamic Multi-page UI**: User Login/Signup -> Dashboard selection Hub -> Upload & Validation with drag-and-drop.

## Design Decisions

- **Two Models vs One**: Separate models allow the CNN to learn highly specific document styles (e.g. prescription headers vs company certificates) without diluting patterns.
- **Confidence-Gated Format Rejection**: Rejects random uploaded images (selfies, landscapes, memes) as "Invalid Format" when CNN prediction confidence falls below 70% (0.70). This leverages the CNN's low confidence on out-of-distribution uploads to avoid false verdicts without training a separate model.
- **Jinja2 Template Inheritance**: Built on a unified layout [base.html](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/app/templates/base.html) with CSS custom variables, glassmorphic styles, flash alerts, and a shared opt-in motion system (`data-tilt`, `data-magnetic`, `data-counter`, `data-sweep`, `data-wobble`, `data-draw`).
- **Motion-Only-When-Allowed**: Every motion primitive short-circuits to its static end-state when `prefers-reduced-motion: reduce` matches. A global CSS rule already collapses `animation-duration` and `transition-duration` to 0.01ms in that case, so the JavaScript controller just opts out of pointer-driven effects.
- **Decoupled Business Logic**: Separation maintained between ELA conversion, model training, prediction, and routing.

## Component Map

### Data Generation
- [generate_synthetic_dataset.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/generate_synthetic_dataset.py) — internship certificates dataset generator.
- [generate_medical_certificates.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/generate_medical_certificates.py) — medical certificates dataset generator.

### Preprocessing
- [ela_converter.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/ela_converter.py) — converts source JPEGs to ELA.

### Training & Prediction
- [train_model.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/train_model.py) — trains CNN for a given certificate type.
- [predict.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/predict.py) — loads and predicts with the correct model.
- [main.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/main.py) — unified CLI entry point.

### Authentication & Routing
- [auth.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/app/auth.py) — user database interactions, password hashing, and login mixins.
- [web_app.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/app/web_app.py) — Flask app, blueprints, login managers, and type-specific routes.

## Route Map
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Root endpoint (auto-redirects to `/login` or `/dashboard`) |
| `/login` | GET/POST | No | Renders login page and authenticates user |
| `/signup` | GET/POST | No | Renders registration page and creates account |
| `/logout` | GET | Yes | Signs out current user session |
| `/dashboard` | GET | Yes | Renders card selection hub for validation models |
| `/validate/<cert_type>` | GET/POST | Yes | Handles certificate uploads and serves results |
