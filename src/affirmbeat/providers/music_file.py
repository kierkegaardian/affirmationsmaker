from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import soundfile as sf

from affirmbeat.dsp.resample import resample_audio


class FileMusicProvider:
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate

    def generate(self, path: str, duration_sec: float, seed: int, bpm: int | None = None) -> np.ndarray:
        file_path = Path(path)
        if not file_path.exists():
            # Fallback for when the user hasn't provided the file yet
            warnings.warn(f"Music file not found: {path}. Using silence.")
            return np.zeros((int(duration_sec * self.sample_rate), 2), dtype=np.float32)

        try:
            audio, sr = sf.read(file_path, dtype="float32")
        except Exception as exc:
            raise RuntimeError(f"Failed to read music file: {file_path}") from exc

        # Handle mono/stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=1)
        elif audio.shape[1] > 2:
            audio = audio[:, :2]

        # Resample if needed
        if sr != self.sample_rate:
            audio = resample_audio(audio, sr, self.sample_rate)

        # Loop to match duration
        target_samples = int(duration_sec * self.sample_rate)
        current_samples = audio.shape[0]
        
        if current_samples < target_samples:
            # Simple tiling loop (crossfade looping is handled by the higher-level builder if configured)
            # But here we just need to provide enough raw audio.
            tile_count = (target_samples // current_samples) + 1
            audio = np.tile(audio, (tile_count, 1))
        
        return audio[:target_samples]
