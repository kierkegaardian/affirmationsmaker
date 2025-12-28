from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from affirmbeat.dsp.pan import apply_pan
from affirmbeat.dsp.limiter import db_to_linear


@dataclass(frozen=True)
class Clip:
    audio: np.ndarray
    start_sample: int
    gain_db: float
    pan: float
    track: str


def place_clips(
    total_samples: int,
    clips: Iterable[Clip],
    sample_rate: int,
) -> dict[str, np.ndarray]:
    tracks: dict[str, np.ndarray] = {}
    for clip in clips:
        if clip.audio.size == 0:
            continue
        start = max(0, clip.start_sample)
        audio = clip.audio
        if audio.ndim == 1:
            stereo = apply_pan(audio, clip.pan)
        else:
            stereo = apply_pan(audio, clip.pan)
        gain = db_to_linear(clip.gain_db)
        stereo = stereo * gain
        end = min(total_samples, start + stereo.shape[0])
        if end <= start:
            continue
        segment = stereo[: end - start]
        buffer = tracks.setdefault(
            clip.track,
            np.zeros((total_samples, 2), dtype=np.float32),
        )
        buffer[start:end] += segment
    return tracks
