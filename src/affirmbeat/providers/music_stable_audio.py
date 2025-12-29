from __future__ import annotations

import inspect
from typing import Any

import numpy as np

from affirmbeat.dsp.resample import resample_audio


class StableAudioOpenProvider:
    def __init__(
        self,
        sample_rate: int,
        model_id: str,
        device: str | None = None,
        steps: int = 100,
        guidance_scale: float | None = None,
        sigma_min: float | None = None,
        sigma_max: float | None = None,
        sampler: str | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.model_id = model_id
        self.device = device
        self.steps = steps
        self.guidance_scale = guidance_scale
        self.sigma_min = sigma_min
        self.sigma_max = sigma_max
        self.sampler = sampler
        self._model = None
        self._config: Any | None = None
        self._device_in_use: str | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            from stable_audio_tools import get_pretrained_model
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "stable-audio-tools and torch are required for stable_audio_open provider"
            ) from exc
        model, config = get_pretrained_model(self.model_id)
        device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        model.eval()
        self._model = model
        self._config = config
        self._device_in_use = device

    def _config_sample_rate(self) -> int | None:
        if self._config is None:
            return None
        if hasattr(self._config, "sample_rate"):
            return int(getattr(self._config, "sample_rate"))
        if isinstance(self._config, dict):
            sr = self._config.get("sample_rate")
            if sr:
                return int(sr)
        return None

    def generate(self, prompt: str, duration_sec: float, seed: int, bpm: int | None) -> np.ndarray:
        self._load()
        try:
            from stable_audio_tools.inference.generation import generate_diffusion_cond
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("stable_audio_tools inference module not available") from exc

        sig = inspect.signature(generate_diffusion_cond)
        step_param = "num_steps" if "num_steps" in sig.parameters else "steps"
        sampler_param = "sampler_type" if "sampler_type" in sig.parameters else "sampler"
        kwargs = {
            "model": self._model,
            "config": self._config,
            "device": self._device_in_use,
            "seed": int(seed),
            step_param: int(self.steps) if step_param in sig.parameters else None,
            sampler_param: self.sampler if sampler_param in sig.parameters else None,
            "sigma_min": self.sigma_min,
            "sigma_max": self.sigma_max,
            "guidance_scale": self.guidance_scale,
        }
        if "conditioning" in sig.parameters:
            conditioning = [{"prompt": prompt, "seconds_total": float(duration_sec)}]
            if bpm is not None:
                conditioning[0]["bpm"] = int(bpm)
            kwargs["conditioning"] = conditioning
        elif "prompt" in sig.parameters:
            kwargs["prompt"] = prompt
            if "seconds_total" in sig.parameters:
                kwargs["seconds_total"] = float(duration_sec)
        filtered = {k: v for k, v in kwargs.items() if v is not None and k in sig.parameters}
        output = generate_diffusion_cond(**filtered)

        result_sr = self._config_sample_rate()
        if isinstance(output, tuple) and len(output) == 2:
            output, result_sr = output

        if hasattr(output, "detach"):
            output = output.detach().cpu().numpy()
        audio = np.asarray(output)
        if audio.ndim == 3:
            audio = audio[0]
        if audio.ndim == 2 and audio.shape[0] in (1, 2) and audio.shape[1] > audio.shape[0]:
            audio = audio.T
        if result_sr and result_sr != self.sample_rate:
            audio = resample_audio(audio, result_sr, self.sample_rate)
        return audio.astype(np.float32)
