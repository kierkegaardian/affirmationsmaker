# Repo Agent Notes

## Precedence
- Follow `/home/user/AGENTS.md` for workspace-wide rules and credential handling.

## Repo Summary
- Path: `/home/user/projects/affirmbeat`.
- Stack: Python audio renderer (TTS + binaural beats); Streamlit UI in `src/affirmbeat/web_ui.py`.

## Common Commands (from README.md)
- Run UI: `streamlit run src/affirmbeat/web_ui.py`.

## Notes
- `.envrc` can set `GEMINI_BIN=gemini`; run `direnv allow` if you use it.
- Uses `pyproject.toml`; tests live in `tests/`.
- Streamlit UI defaults to `http://localhost:8501` (set `STREAMLIT_SERVER_PORT` to override).
- Uses Ollama at `http://127.0.0.1:11434`.

## Quality
- **Typesafety (Request):** Enforce robust, stack-appropriate typesafety in all changes (Python type hints + pyright/mypy when applicable).
