# Plan Options — affirmations-builder

## Option A: Minimal renderer fix
Focus on unblocking renders quickly with the smallest set of changes.
- Fix missing imports in `render/renderer.py`.
- Implement `_music_provider` to return placeholder/file/stable providers.
- Pass `MusicConfig` values into `StableAudioOpenProvider`.
- No tests; rely on manual verification.

Pros: fastest, least code churn.
Cons: no automated guardrail for regressions.

## Option B: Renderer fix + smoke tests
Stabilize the renderer and add lightweight tests to keep it working.
- Everything in Option A.
- Add `tests/test_render_smoke.py` using `unittest`:
  - Dummy TTS + placeholder music render to temp dir.
  - File music provider renders from a tiny generated WAV.
- Document a single test command.

Pros: catches import/provider regressions; still small scope.
Cons: adds test runtime (requires soundfile/libsndfile).

## Option C: Fix + validation polish
Include user-facing validation to reduce runtime failures.
- Everything in Option B.
- Validate `music.provider` and `tts.provider` with clearer errors.
- In CLI TUI, block `piper1` unless a model path is provided.

Pros: better UX for CLI; fewer runtime surprises.
Cons: more behavior changes; more prompts to handle.
