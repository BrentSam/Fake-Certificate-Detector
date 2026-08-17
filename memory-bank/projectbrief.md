# Project Brief

## Project Name

Fake Certificate Detector

## Purpose

Build a tool that helps users assess whether a certificate document is likely authentic or suspicious. The system supports **two certificate types** — internship certificates and medical certificates — each with a dedicated detection model. Users access the tool through a secure web interface with login/signup and a dashboard for certificate type selection.

## Primary Goals

- Accept certificate evidence from users in a practical format (image files).
- Support **two specialized detection models**: one for internship certificates and one for medical certificates.
- Provide clear results: Real/Fake verdict, confidence percentage, and fake probability.
- Require user authentication (login/signup) before accessing detection features.
- Present a modern, premium dashboard UI with certificate type selection.
- Keep the workflow transparent: distinguish between verified facts, heuristic warnings, and uncertain results.
- Avoid presenting a detection result as legal proof unless backed by a verified source.

## Non-Goals

- Do not store credentials, private keys, or sensitive identity data in project memory.
- Do not claim guaranteed authenticity unless the system has an authoritative verification source.
- Do not depend on undocumented third-party services without recording the decision in `techContext.md`.
- Do not store uploaded certificates beyond the validation session.

## Success Criteria

- A user can sign up, log in, select a certificate type, upload a certificate, and receive a clear assessment.
- Two separate models are trained and perform reasonably on their respective certificate types.
- Detection logic is testable and produces consistent outputs for known valid, invalid, and ambiguous examples.
- The project documentation keeps future agents aligned on product intent, architecture, and current work.

## Current State

The project has a working single-model prototype with synthetic data generation, ELA preprocessing, EfficientNetB0 training (83% accuracy), CLI prediction, and a basic Flask upload UI. An implementation plan has been created for the multi-model + auth + dashboard expansion, pending user approval.
