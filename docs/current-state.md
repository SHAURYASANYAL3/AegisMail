# Current State & Baseline Audit

**Date**: 2026-09-10  
**Host Architecture**: Apple M4 (16 GB Unified Memory, arm64 macOS)  
**Runtimes**:
- Python: `3.13.14`
- Node.js: `v26.7.0`
- npm: `11.19.0`
- Git: Initialized on `main` branch with zero prior commits.

## Dependency Strategy
Following the `managing-python-dependencies` protocol:
- Dedicated virtual environment at `.venv` created with `python3 -m venv .venv`.
- Packages managed via explicit `.venv/bin/pip` and pinned in `requirements.txt`.
- Frontend dependencies managed via `package.json` in `frontend/` using `npm`.

## Zero-Cost & Offline Guarantee
- The core platform runs 100% locally with zero required external API keys ($0 operational cost).
- Full forensic workflow functions offline in `DEMO_MODE=true` with synthetic intelligence datasets.
