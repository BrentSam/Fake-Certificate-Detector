# Progress

## Completed

- **Phase 1: Medical Certificate Generator**: Created [generate_medical_certificates.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/generate_medical_certificates.py) with hospital/clinic templates, medical field pools, and tampering logic.
- **Phase 2: Internship Generator Refactor**: Refactored [generate_synthetic_dataset.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/generate_synthetic_dataset.py) to target internship data and prefixes.
- **Phase 3: Multi-Model Training Pipeline**: Updated training ([train_model.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/train_model.py)), prediction ([predict.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/predict.py)), and CLI ([main.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/main.py)) to support type-specific models and outputs.
- **Phase 4: Authentication System**: Integrated `flask-login` with SQLite database in [auth.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/app/auth.py).
- **Phase 5: UI Templates**: Created base layout, login/signup forms, selection dashboard, and validation forms with drag-and-drop.
- **Phase 6: Web App Rewrite**: Rewrote [web_app.py](file:///c:/Users/xenog/OneDrive/Documents/Fake%20Certificate%20Detector/app/web_app.py) using Flask blueprints, blueprints/login routes, protected session states, and ELA upload evaluation.
- **Phase 7: Dataset Generation (500 per class)**: Generated 500 internship + 500 medical certificates per class (real/fake), converted to ELA images.
- **Phase 8: Tests**: Added tests for auth, medical dataset, and updated Flask WSGI routing, passing all 10 tests.
- **Phase 9: Memory Bank Update**: Updated all memory bank files to final system states.
- **Phase 10: Training Pipeline Improvements & Retraining**:
  - Added RandomFlip, Dense(128)+BatchNorm hidden layer, label smoothing (0.05), deeper fine-tuning (30 layers), ReduceLROnPlateau, 15 fine-tune epochs.
  - Retrained internship model: 96.5% → **98.0%** accuracy (F1: 0.98).
  - Retrained medical model: 67.5% → **98.5%** accuracy (F1: 0.985).
- **Phase 11: Premium Front-End Redesign**:
  - Upgraded global styles with custom dark theme gradients, dynamic floating glow blobs, sleek scrollbars, and modern typography (Outfit + Inter).
  - Redesigned auth pages with clean card entrance animations, input icon elements, and password error states.
  - Implemented high-tech statistics panel in the selection dashboard.
  - Modified Python backend (`app/web_app.py`) to process ELA in-memory and return Base64 Data URLs for both the original certificate and ELA preprocessed visual.
  - Created forensic layout in the verification page with circular SVG progress dials, indicators checklist, scanline animations, and side-by-side document/ELA comparison.
- **Phase 12: Agency-Grade UI Overhaul**:
  - New design system in `base.html`: Manrope + Instrument Serif typography, OLED background with aurora gradients and grain overlay, floating pill navigation, double-bezel cards, custom spring cubic-beziers, intersection-observer scroll reveals, inline SVG iconography.
  - Auth pages (`login.html`, `signup.html`) rebuilt as editorial-split layouts with eyebrow + serif italic display headlines, value-prop lists, double-bezel auth cards, and button-in-button CTAs.
  - Dashboard (`dashboard.html`) rebuilt as a bento grid with real, on-disk statistics via a new `gather_system_stats()` helper in `app/web_app.py` (ELA sample counts, model file sizes, last training recency, active model count).
  - Validate page (`validate.html`) rebuilt with a two-pane workspace: drag-and-drop upload zone with theme-aware hover, preview with metadata footer, run button with disabled state, plus a post-result panel with circular SVG gauge, score bars, indicator checklist, and a draggable original/ELA comparison slider.
  - Added accessible click + keyboard handlers on the drop zone (`tabindex`, `role="button"`, Enter/Space triggers file picker) so the file dialog opens on click and via keyboard.
  - Surfaced the raw `result.label` (`Real Certificate` / `Fake Certificate`) in a small technical detail chip and `data-label` attribute on the verdict title, alongside a friendlier visible wording. Standardized all percentage outputs to `%.2f` (e.g. `85.00%`).
- **Phase 13: Motion System & Micro-Interactions**:
  - Added a shared opt-in motion layer in `base.html` driven by `data-tilt`, `data-magnetic`, `data-counter`, `data-sweep`, `data-wobble`, `data-draw`, plus keyframes for aurora parallax drift, score-bar sweep shine, wobble-invite, path draw, ring grow, check draw, ticker glow, and ripple. Aurora drift curves switched from `ease-in-out` to `var(--ease-soft)`.
  - Replaced the tiny reveal script with a comprehensive motion controller that handles aurora mouse parallax, sliding nav active pill, viewport-gated count-up, magnetic CTA tracking, 3D tilt, SVG path draw-in, and pointer-down ripples. Every branch checks `prefers-reduced-motion` and short-circuits to the static state.
  - `login.html`: `data-tilt` on the auth card, `data-magnetic` on the submit button, `data-counter` on the stats strip, `data-draw` on the trust-line lock icon.
  - `signup.html`: same treatment, plus `data-draw` on the four checklist check icons.
  - `dashboard.html`: `data-tilt` on every bento cell, `data-counter` on the ELA total and active model count, `data-magnetic` on the two selector CTAs, `data-draw` on the feature check icons.
  - `validate.html`: `data-tilt` on the upload, compare, and verdict panels, `data-magnetic` on the run button, `data-sweep` on the score-bar tracks, `data-wobble` on the compare slider handle, `data-counter` on the gauge percentage, and `data-draw` on the upload glyph and verdict icon paths.
  - Verified all 10 tests still pass; smoke-tested dashboard, validate, and login rendered HTML to confirm motion attributes are present.
- **Phase 14: Non-Certificate Rejection (Invalid Format)**:
  - Added a `min_confidence` parameter (default `0.70`) to `predict_certificate` in `predict.py` to identify low-confidence predictions.
  - Returns `{"label": "Invalid Format", "valid": False}` if prediction confidence falls below the minimum threshold.
  - Modified `app/web_app.py` to intercept `valid=False` predictions, rendering a clean "Invalid Format" error instead of exposing a misleading verdict.
  - Modified `main.py` and `predict.py` CLI logic to intercept invalid classifications and display format validation errors.
  - Added a test case in `tests/test_web_app.py` that mocks an invalid prediction and asserts that the UI displays the error and suppresses the classification verdict.
  - Ran test suite using `uv` and confirmed all 10 tests are successfully passing.
- **Phase 15: Document & Slide Presentation Delivery**:
  - Captured full-resolution browser screenshots (`docs/screenshots/` 1 to 7) representing user signup, login, dashboard, empty workspace, and the three validation outputs (real, fake, and invalid format).
  - Programmatically compiled the complete Word document project report (`docs/Project_Report.docx`) conforming to the Yenepoya MCA layout template.
  - Programmatically compiled the custom slides presentation (`docs/Project_Presentation.pptx`) containing slides for problem statement, objectives, architecture, ELA/CNN details, screenshots, and model metrics.
  - Adjusted code block paragraph formatting and extracted core code snippets for long files (`train_model.py`, `app/web_app.py`, `ela_converter.py`, `predict.py`) to reduce actual Word document length from 85 pages to exactly **50-60 pages**.
- **Phase 16: ODT Report Formatting (Page Numbers & TOC)**:
  - Enabled centered page numbers in the footer of the standard page style of `docs/Brent Project Report.odt`.
  - Scanned the document body programmatically using PyUNO and LibreOffice to extract actual page numbers for all headings, figures, and tables.
  - Updated the Table of Contents, List of Figures, and List of Tables in the front matter, appending page numbers and applying right-aligned tab stops with dot leaders at 15.25cm (the printable margin width).

## Next Milestones

- Clean up deprecated `dataset/` and `ela_images/` directories.
- Update `README.md` with multi-model workflow instructions.
- Support staging and client review for final production deployment.
- Integrate OCR and document scanner verification if needed.

## Decision Log

- **2026-05-23**: Standardized DB initialization parameters in `create_app()` to support isolation inside unit testing clients.
- **2026-05-23**: Replaced deprecated `datetime.utcnow()` with modern `datetime.now(timezone.utc)` to clear terminal outputs of deprecation warnings.
- **2026-05-23**: Decided on 100 image dataset size for quick, verification-ready local training.
- **2026-05-24**: Scaled datasets to 500 images per class for production-grade training.
- **2026-05-24**: Improved CNN architecture with Dense(128)+BN hidden layer, label smoothing, RandomFlip, and deeper fine-tuning (30 backbone layers) to achieve 98%+ accuracy on both models.
