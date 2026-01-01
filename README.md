# AffirmBeat Studio (MVP)

Local-first audio renderer for affirmation sessions: TTS + binaural beats + placeholder music bed.

## Quick start

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .

affirmbeat init projects/my_project.json
affirmbeat render projects/my_project.json
```

Outputs land in `projects/output/` by default.

## CLI spec (v0)

- `affirmbeat init <project.json>`
- `affirmbeat add-affirmation <project.json> "text" --tag <tag>`
- `affirmbeat tui [project.json]` (interactive wizard)
- `affirmbeat generate-tracks <project.json> --prompt "..."`
- `affirmbeat render <project.json>`

Expected outputs:

- `projects/output/final.wav`
- `projects/output/stems/*.wav`
- `projects/output/render_report.json`

## Linux prerequisites

The Python `soundfile` dependency requires `libsndfile` on Linux. Install it with your package manager, for example:

- Debian/Ubuntu: `libsndfile1` (runtime) and `libsndfile1-dev` (build headers, if needed)
- Fedora/RHEL: `libsndfile`
- Arch: `libsndfile`

Optional binaries are only needed when you select the corresponding provider:

- `espeak`/`espeak-ng` for `tts.provider = "espeak"`.
- `piper` for `tts.provider = "piper1"` (with `tts.model_path`).

## Notes

- Default TTS provider is `dummy` (sine-tone placeholder). To use Piper, install the `piper` binary and set `tts.provider` to `piper1` with `tts.model_path`.
- Local-only alternative TTS: set `tts.provider` to `espeak` (requires `espeak` or `espeak-ng` in PATH).
- Music provider defaults to placeholder noise. For Stable Audio Open, set `music.provider` to `stable_audio_open` and install `stable-audio-tools` + `torch`.
- Render reports include `content_warnings` for possible negations/negative phrasing; it is non-blocking.
- `affirmbeat tui` writes `voice_tracks` in `project.json`. Rendering uses `voice_tracks` when present; otherwise it falls back to `affirmations`.
- LLM track generation uses a local Ollama instance by default (`OLLAMA_HOST`).

Stable Audio Open dependencies currently install cleanly on Python 3.10/3.11. If you use `uv`, a working setup is:

```bash
uv python install 3.10
uv venv .venv310 --python 3.10
source .venv310/bin/activate
python -m pip install stable-audio-tools torch
```
