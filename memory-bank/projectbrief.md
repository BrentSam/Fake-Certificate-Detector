# Project Brief

## Project Name

Fake Certificate Detector

## Purpose

Build a tool that helps users assess whether a certificate document is likely authentic or suspicious. The project should support a clear, repeatable detection workflow and explain findings in a way that a non-expert user can understand.

## Primary Goals

- Accept certificate evidence from users in a practical format, likely image or PDF files.
- Extract or inspect relevant certificate details such as issuer, holder name, dates, identifiers, signatures, seals, layout, and visible inconsistencies.
- Flag suspicious indicators and provide understandable reasons.
- Keep the workflow transparent: distinguish between verified facts, heuristic warnings, and uncertain results.
- Avoid presenting a detection result as legal proof unless backed by a verified source.

## Non-Goals

- Do not store credentials, private keys, or sensitive identity data in project memory.
- Do not claim guaranteed authenticity unless the system has an authoritative verification source.
- Do not depend on undocumented third-party services without recording the decision in `techContext.md`.

## Success Criteria

- A user can submit a certificate and receive a clear assessment with evidence-backed observations.
- Detection logic is testable and produces consistent outputs for known valid, invalid, and ambiguous examples.
- The project documentation keeps future agents aligned on product intent, architecture, and current work.

## Current State

The project workspace has been initialized with a Memory Bank, `AGENTS.md`, and a Python prototype for synthetic data generation, ELA preprocessing, CNN training, prediction, optional Flask upload UI, documentation, and lightweight tests. A first synthetic-data baseline has been trained locally; real-world performance still requires consented/anonymized certificate data.
