from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf

from affirmbeat.dsp.resample import resample_audio


class EspeakTTSProvider:
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate

    def list_voices(self) -> list[str]:
        binary = shutil.which("espeak") or shutil.which("espeak-ng")
        if not binary:
            return []
        result = subprocess.run([binary, "--voices"], capture_output=True, text=True, check=False)
        lines = result.stdout.splitlines()
        voices: list[str] = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4:
                voices.append(parts[3])
        return voices

    def synthesize(self, text: str, voice: str | None, settings: dict) -> object:
        binary = shutil.which("espeak") or shutil.which("espeak-ng")
        if not binary:
            raise RuntimeError("espeak binary not found in PATH")
        rate = float(settings.get("rate", 1.0))
        speed_wpm = max(80, int(175 * rate))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "tts.wav"
            cmd = [binary, "-s", str(speed_wpm), "-w", str(output_path)]
            if voice:
                cmd += ["-v", voice]
            cmd.append(text)
            subprocess.run(cmd, check=True)
            audio, sr = sf.read(output_path, dtype="float32")
            if sr != self.sample_rate:
                audio = resample_audio(audio, sr, self.sample_rate)
            return audio
