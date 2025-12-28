from __future__ import annotations

import math
import numpy as np
from scipy.signal import resample_poly


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return audio.astype(np.float32)
    if audio.size == 0:
        return audio.astype(np.float32)
    if audio.ndim == 1:
        audio = audio[:, None]
    gcd = math.gcd(orig_sr, target_sr)
    up = target_sr // gcd
    down = orig_sr // gcd
    resampled = []
    for ch in range(audio.shape[1]):
        resampled.append(resample_poly(audio[:, ch], up, down))
    stacked = np.stack(resampled, axis=1)
    if stacked.shape[1] == 1:
        return stacked[:, 0].astype(np.float32)
    return stacked.astype(np.float32)
