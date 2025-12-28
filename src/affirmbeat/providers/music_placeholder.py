from __future__ import annotations

import numpy as np


class PlaceholderMusicProvider:
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate

    def generate(self, prompt: str, duration_sec: float, seed: int, bpm: int | None) -> np.ndarray:
        total_samples = int(duration_sec * self.sample_rate)
        if total_samples <= 0:
            return np.zeros((0, 2), dtype=np.float32)
        rng = np.random.default_rng(seed)
        noise = rng.normal(0.0, 0.02, size=(total_samples, 2)).astype(np.float32)
        return noise
