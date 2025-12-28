from __future__ import annotations

import numpy as np


def db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)


def apply_peak_limiter(audio: np.ndarray, peak_db: float) -> np.ndarray:
    if audio.size == 0:
        return audio
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    limit = db_to_linear(peak_db)
    if peak <= limit:
        return audio
    gain = limit / peak
    return audio * gain
