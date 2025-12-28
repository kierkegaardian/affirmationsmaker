from __future__ import annotations

import numpy as np


def apply_fade(audio: np.ndarray, fade_in_samples: int, fade_out_samples: int) -> np.ndarray:
    if audio.size == 0:
        return audio
    total = audio.shape[0]
    output = audio.copy()
    if fade_in_samples > 0:
        fade_in = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, fade_in_samples))
        output[:fade_in_samples] *= fade_in[:, None]
    if fade_out_samples > 0:
        fade_out = 0.5 - 0.5 * np.cos(np.linspace(np.pi, 0.0, fade_out_samples))
        output[-fade_out_samples:] *= fade_out[:, None]
    return output


def equal_power_fade(fade_samples: int) -> tuple[np.ndarray, np.ndarray]:
    if fade_samples <= 0:
        return np.array([], dtype=np.float32), np.array([], dtype=np.float32)
    t = np.linspace(0.0, 1.0, fade_samples, dtype=np.float32)
    fade_in = np.sin(0.5 * np.pi * t)
    fade_out = np.cos(0.5 * np.pi * t)
    return fade_in, fade_out
