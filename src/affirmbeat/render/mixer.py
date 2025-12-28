from __future__ import annotations

import numpy as np

from affirmbeat.dsp.limiter import apply_peak_limiter
from affirmbeat.dsp.loudness import apply_loudness


def mix_tracks(
    tracks: dict[str, np.ndarray],
    master_peak_db: float,
    sample_rate: int,
    target_lufs: float | None,
) -> np.ndarray:
    if not tracks:
        return np.zeros((0, 2), dtype=np.float32)
    total_samples = max(track.shape[0] for track in tracks.values())
    mix = np.zeros((total_samples, 2), dtype=np.float32)
    for track_audio in tracks.values():
        mix[: track_audio.shape[0]] += track_audio
    if target_lufs is not None:
        mix = apply_loudness(mix, sample_rate, target_lufs)
    mix = apply_peak_limiter(mix, master_peak_db)
    return mix.astype(np.float32)
