# Change Proposal: affirmations-builder

## Summary
Stabilize the renderer so the CLI/Web UI can reliably produce the expected WAV
outputs and render report from README’s CLI spec.

## Motivation
The core render pipeline currently crashes due to missing imports and incomplete
music-provider selection, which blocks `affirmbeat render` and the Streamlit UI.

## Scope
### In scope
- Fix renderer imports and provider selection so `affirmbeat render` works.
- Support placeholder, file, and stable-audio music providers in the renderer.
- Add minimal smoke tests for rendering with dummy TTS + placeholder music.

### Out of scope
- UI redesigns or new providers beyond placeholder/file/stable-audio.
- Performance optimization or audio quality tuning.

## Acceptance criteria
- `affirmbeat render projects/demo_project.json` completes and writes:
  - `projects/output/final.wav`
  - `projects/output/stems/*.wav`
  - `projects/output/render_report.json`
- Streamlit UI render completes without runtime errors.
- Placeholder music provider produces audio when selected.

## Risks
- Optional dependencies (stable-audio-tools/torch) may be missing; failures
  must remain isolated to that provider.
