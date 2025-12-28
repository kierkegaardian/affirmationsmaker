from __future__ import annotations

import numpy as np

from affirmbeat.dsp.fades import apply_fade


class DummyTTSProvider:
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate

    def list_voices(self) -> list[str]:
        return ["dummy"]

    def synthesize(self, text: str, voice: str | None, settings: dict) -> np.ndarray:
        rate = float(settings.get("rate", 1.0))
        words = max(1, len(text.split()))
        duration = max(0.3, words * 0.35 / max(rate, 0.1))
        total_samples = int(duration * self.sample_rate)
        time = np.arange(total_samples, dtype=np.float32) / self.sample_rate
        freq = 220.0 + (len(text) % 5) * 30.0
        audio = 0.2 * np.sin(2 * np.pi * freq * time)
        audio = audio.astype(np.float32)
        audio = apply_fade(audio[:, None], int(0.01 * self.sample_rate), int(0.05 * self.sample_rate))
        return audio[:, 0]
