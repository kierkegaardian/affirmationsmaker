# AffirmBeat Studio (MVP)

Local-first audio renderer for affirmation sessions: TTS + binaural beats + placeholder music bed.

## Quick start

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .

affirmbeat init projects/demo_project.json
affirmbeat render projects/demo_project.json
```

Outputs land in `projects/output/` by default.

## CLI spec (v0)

- `affirmbeat init <project.json>`
- `affirmbeat add-affirmation <project.json> "text" --tag <tag>`
- `affirmbeat render <project.json>`

Expected outputs:

- `projects/output/final.wav`
- `projects/output/stems/*.wav`
- `projects/output/render_report.json`

## Notes

- Default TTS provider is `dummy` (sine-tone placeholder). To use Piper, install the `piper` binary and set `tts.provider` to `piper1` with `tts.model_path`.
- Local-only alternative TTS: set `tts.provider` to `espeak` (requires `espeak` or `espeak-ng` in PATH).
- Music provider defaults to placeholder noise. For Stable Audio Open, set `music.provider` to `stable_audio_open` and install `stable-audio-tools` + `torch`.
- Render reports include `content_warnings` for possible negations/negative phrasing; it is non-blocking.

Stable Audio Open dependencies currently install cleanly on Python 3.10/3.11. If you use `uv`, a working setup is:

```bash
uv python install 3.10
uv venv .venv310 --python 3.10
source .venv310/bin/activate
python -m pip install stable-audio-tools torch
```
