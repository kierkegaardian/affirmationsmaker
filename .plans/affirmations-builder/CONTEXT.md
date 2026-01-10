# Architect Context Pack (affirmations-builder)

## Source of truth
- Project conventions: `openspec/project.md`
- Approved proposal: `openspec/changes/affirmations-builder/proposal.md`
- Task list: `openspec/changes/affirmations-builder/tasks.md`
- Design notes (optional): `openspec/changes/affirmations-builder/design.md`
- Spec deltas (optional): `openspec/changes/affirmations-builder/specs/`

## Invariants (fill in)
- Render outputs must land under `projects/output/`.
- Provider selection stays in `src/affirmbeat/render/renderer.py`.
- Cache artifacts live under `projects/cache/` (or `AFFIRMBEAT_CACHE_DIR`).

## Entrypoints (fill in)
- CLI: `src/affirmbeat/cli/main.py`
- Streamlit UI: `src/affirmbeat/web_ui.py`
- Renderer: `src/affirmbeat/render/renderer.py`

## Verification commands (fill in)
- `python -m unittest discover -s tests`
- `affirmbeat render projects/demo_project.json`
