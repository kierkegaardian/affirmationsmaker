# Project Context

## Overview
AffirmBeat Studio is a local-first affirmation audio renderer (CLI + Streamlit UI)
that turns project JSON files into WAV outputs (voice, music bed, binaural beats,
and a render report). "Done" means CLI and UI render successfully and produce
`projects/output/final.wav`, `projects/output/stems/*.wav`, and `render_report.json`.

## Tech stack
- Language(s): Python 3.10+
- Framework(s): Typer CLI, Streamlit UI, Pydantic v2 models
- Build/test commands:
  - `pip install -e .`
  - `streamlit run src/affirmbeat/web_ui.py`
  - `affirmbeat render projects/demo_project.json`

## Conventions
- Folder structure: `src/affirmbeat` (core, providers, render, dsp, cli)
- Naming: snake_case modules; config models in `core/project.py`

## Architecture constraints (invariants)
- Render pipeline goes through `render/renderer.py` and writes outputs to `projects/output/`.
- Provider selection stays centralized in `render/renderer.py`.
- Cache artifacts live under `projects/cache/` (or `AFFIRMBEAT_CACHE_DIR` override).

## Verification
- Unit tests: `python -m unittest discover -s tests`
- Integration/E2E: `affirmbeat render projects/demo_project.json`
