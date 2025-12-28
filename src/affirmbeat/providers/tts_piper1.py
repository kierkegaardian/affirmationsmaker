from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf

from affirmbeat.dsp.resample import resample_audio


class PiperTTSProvider:
    def __init__(self, sample_rate: int, model_path: str | None = None) -> None:
        self.sample_rate = sample_rate
        self.model_path = model_path

    def list_voices(self) -> list[str]:
        return []

    def synthesize(self, text: str, voice: str | None, settings: dict) -> object:
        binary = shutil.which("piper")
        if not binary:
            raise RuntimeError("piper binary not found in PATH")
        model = settings.get("model_path") or self.model_path or voice
        if not model:
            raise RuntimeError("piper model_path or voice is required")
        length_scale = 1.0 / max(0.1, float(settings.get("rate", 1.0)))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "tts.wav"
            cmd = [
                binary,
                "--model",
                str(model),
                "--output_file",
                str(output_path),
                "--length_scale",
                str(length_scale),
            ]
            subprocess.run(cmd, input=text.encode("utf-8"), check=True)
            audio, sr = sf.read(output_path, dtype="float32")
            if sr != self.sample_rate:
                audio = resample_audio(audio, sr, self.sample_rate)
            return audio
