from __future__ import annotations

import math
import numpy as np


def pan_mono_to_stereo(audio: np.ndarray, pan: float) -> np.ndarray:
    pan = max(-1.0, min(1.0, pan))
    angle = (pan + 1.0) * (math.pi / 4.0)
    left_gain = math.cos(angle)
    right_gain = math.sin(angle)
    left = audio * left_gain
    right = audio * right_gain
    return np.stack([left, right], axis=1)


def apply_pan(audio: np.ndarray, pan: float) -> np.ndarray:
    if audio.ndim == 1:
        return pan_mono_to_stereo(audio, pan)
    if audio.ndim == 2 and audio.shape[1] == 2:
        pan = max(-1.0, min(1.0, pan))
        angle = (pan + 1.0) * (math.pi / 4.0)
        left_gain = math.cos(angle) * math.sqrt(2.0)
        right_gain = math.sin(angle) * math.sqrt(2.0)
        stereo = audio.copy()
        stereo[:, 0] *= left_gain
        stereo[:, 1] *= right_gain
        return stereo
    raise ValueError("Audio must be mono or stereo")
