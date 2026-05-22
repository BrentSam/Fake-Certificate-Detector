# Agent Instructions

This project uses the Memory Bank workflow described in the Agentic Coding Handbook:
https://tweag.github.io/agentic-coding-handbook/WORKFLOW_MEMORY_BANK/

## Required Startup Routine

At the start of every agent session:

1. Read every file in `memory-bank/`.
2. Treat the Memory Bank as the project's long-term working context.
3. Prefer the Memory Bank over assumptions when choosing architecture, tooling, and next steps.
4. If the Memory Bank conflicts with the code, inspect the code and update the Memory Bank as part of the task.

## Memory Bank Files

- `memory-bank/projectbrief.md`: Project scope, goals, and success criteria.
- `memory-bank/productContext.md`: Users, problems, UX goals, and product behavior.
- `memory-bank/systemPatterns.md`: Architecture, design patterns, and decisions.
- `memory-bank/techContext.md`: Stack, tooling, dependencies, setup, and constraints.
- `memory-bank/activeContext.md`: Current work, recent changes, open questions, and next steps.
- `memory-bank/progress.md`: Completed work, pending work, blockers, and decision log.

## Update Rules

- Update `memory-bank/activeContext.md` whenever the current focus, next steps, or known issues change.
- Update `memory-bank/progress.md` after meaningful implementation, bug fixes, design decisions, or verification work.
- Update `memory-bank/systemPatterns.md` and `memory-bank/techContext.md` when architecture or tooling changes.
- Keep entries concise and structured. Reference files by path instead of pasting large code blocks.
- Never store secrets, credentials, private keys, tokens, database URLs, or raw chat transcripts in the Memory Bank.

## Project Working Norms

- This project is named `Fake Certificate Detector`.
- Until implementation exists, preserve the current Memory Bank assumptions as provisional.
- Favor small, verifiable changes and update the Memory Bank alongside code changes.
- Add or update tests when introducing detection logic, parsing behavior, file handling, or UI workflows.
