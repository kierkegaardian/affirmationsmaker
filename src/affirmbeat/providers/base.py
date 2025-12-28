from __future__ import annotations

from typing import Protocol
import numpy as np


class TTSProvider(Protocol):
    def list_voices(self) -> list[str]:
        ...

    def synthesize(self, text: str, voice: str | None, settings: dict) -> np.ndarray:
        ...


class MusicProvider(Protocol):
    def generate(
        self,
        prompt: str,
        duration_sec: float,
        seed: int,
        bpm: int | None,
    ) -> np.ndarray:
        ...
