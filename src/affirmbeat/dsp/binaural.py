from __future__ import annotations

import numpy as np

from affirmbeat.dsp.fades import apply_fade
from affirmbeat.dsp.limiter import db_to_linear


def generate_binaural(
    duration_sec: float,
    sample_rate: int,
    carrier_hz: float,
    beat_hz: float,
    gain_db: float,
    fade_in_ms: int,
    fade_out_ms: int,
) -> np.ndarray:
    total_samples = int(duration_sec * sample_rate)
    if total_samples <= 0:
        return np.zeros((0, 2), dtype=np.float32)
    time = np.arange(total_samples, dtype=np.float32) / sample_rate
    left_freq = carrier_hz - beat_hz / 2.0
    right_freq = carrier_hz + beat_hz / 2.0
    left = np.sin(2 * np.pi * left_freq * time)
    right = np.sin(2 * np.pi * right_freq * time)
    stereo = np.stack([left, right], axis=1)
    stereo *= db_to_linear(gain_db)
    fade_in_samples = int((fade_in_ms / 1000.0) * sample_rate)
    fade_out_samples = int((fade_out_ms / 1000.0) * sample_rate)
    stereo = apply_fade(stereo, fade_in_samples, fade_out_samples)
    return stereo.astype(np.float32)
