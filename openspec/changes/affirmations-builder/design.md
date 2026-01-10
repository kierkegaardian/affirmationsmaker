# Design Notes

## Decisions
- Keep provider selection centralized in `render/renderer.py`.
- Default unknown music providers to `PlaceholderMusicProvider` with a clear error.

## Alternatives considered
- Moving provider selection into `core/project` validation (rejected: runtime deps).
