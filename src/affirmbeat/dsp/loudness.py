from __future__ import annotations

import numpy as np

try:
    import pyloudnorm as pyln
except Exception:  # pragma: no cover - optional dependency behavior
    pyln = None


def apply_loudness(audio: np.ndarray, sample_rate: int, target_lufs: float) -> np.ndarray:
    if pyln is None:
        return audio
    meter = pyln.Meter(sample_rate)
    loudness = meter.integrated_loudness(audio)
    normalized = pyln.normalize.loudness(audio, loudness, target_lufs)
    return normalized.astype(np.float32)
