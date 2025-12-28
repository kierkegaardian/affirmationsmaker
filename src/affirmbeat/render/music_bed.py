from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from affirmbeat.core.hashing import hash_dict
from affirmbeat.core.paths import cache_dir
from affirmbeat.core.project import Project
from affirmbeat.dsp.fades import equal_power_fade


def _ensure_stereo(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return np.stack([audio, audio], axis=1)
    if audio.ndim == 2 and audio.shape[1] == 2:
        return audio
    if audio.ndim == 2 and audio.shape[0] == 2:
        return audio.T
    if audio.ndim == 2 and audio.shape[1] == 1:
        return np.repeat(audio, 2, axis=1)
    raise ValueError("Unsupported audio shape for music")


def _pad_or_trim(audio: np.ndarray, target_samples: int) -> np.ndarray:
    if audio.shape[0] == target_samples:
        return audio
    if audio.shape[0] > target_samples:
        return audio[:target_samples]
    pad = np.zeros((target_samples - audio.shape[0], audio.shape[1]), dtype=np.float32)
    return np.concatenate([audio, pad], axis=0)


def _crossfade_two(a: np.ndarray, b: np.ndarray, fade_samples: int) -> np.ndarray:
    if fade_samples <= 0:
        return np.concatenate([a, b], axis=0)
    fade = min(fade_samples, a.shape[0], b.shape[0])
    if fade <= 0:
        return np.concatenate([a, b], axis=0)
    fade_in, fade_out = equal_power_fade(fade)
    fade_in = fade_in[:, None]
    fade_out = fade_out[:, None]
    blended = a[-fade:] * fade_out + b[:fade] * fade_in
    return np.concatenate([a[:-fade], blended, b[fade:]], axis=0)


def _music_cache_key(
    project: Project,
    prompt: str,
    seed: int,
    duration_sec: float,
    chunk_index: int,
) -> str:
    return hash_dict(
        {
            "provider": project.music.provider,
            "prompt": prompt,
            "seed": seed,
            "duration_sec": duration_sec,
            "chunk_index": chunk_index,
            "sample_rate": project.sample_rate,
            "model_id": project.music.model_id,
            "steps": project.music.steps,
            "guidance_scale": project.music.guidance_scale,
            "sigma_min": project.music.sigma_min,
            "sigma_max": project.music.sigma_max,
            "sampler": project.music.sampler,
            "bpm": project.music.bpm,
        }
    )


def _load_or_generate_music_chunk(
    project: Project,
    project_path: Path,
    provider,
    duration_sec: float,
    seed: int,
    chunk_index: int,
    report: dict[str, Any],
) -> np.ndarray:
    cache_root = cache_dir(project_path) / "music"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_key = _music_cache_key(project, project.music.prompt, seed, duration_sec, chunk_index)
    cache_path = cache_root / f"{cache_key}.wav"
    if cache_path.exists():
        audio, _ = sf.read(cache_path, dtype="float32")
        report["music_cached"].append(cache_path.name)
        return audio
    audio = provider.generate(
        project.music.prompt,
        duration_sec,
        seed,
        project.music.bpm,
    )
    sf.write(cache_path, audio, project.sample_rate)
    report["music_generated"].append(cache_path.name)
    return audio


def build_music_bed(project: Project, project_path: Path, provider, report: dict[str, Any]) -> np.ndarray:
    total_samples = int(project.duration_sec * project.sample_rate)
    if total_samples <= 0:
        return np.zeros((0, 2), dtype=np.float32)
    chunk_sec = min(project.music.chunk_sec, project.duration_sec)
    if chunk_sec <= 0:
        return np.zeros((total_samples, 2), dtype=np.float32)
    fade_sec = max(0.0, project.music.crossfade_ms / 1000.0)
    if project.music.build_mode != "loop_crossfade":
        chunk_sec = project.duration_sec
        fade_sec = 0.0
    fade_samples = int(fade_sec * project.sample_rate)

    output: np.ndarray | None = None
    idx = 0
    while output is None or output.shape[0] < total_samples:
        gen_sec = chunk_sec
        if output is not None and fade_samples > 0:
            gen_sec = chunk_sec + fade_sec
        seed = project.music.seed + idx
        chunk = _load_or_generate_music_chunk(
            project,
            project_path,
            provider,
            gen_sec,
            seed,
            idx,
            report,
        )
        chunk = _ensure_stereo(chunk)
        chunk = _pad_or_trim(chunk, int(gen_sec * project.sample_rate))
        if output is None:
            output = chunk
        else:
            output = _crossfade_two(output, chunk, fade_samples)
        idx += 1
    output = _pad_or_trim(output, total_samples)
    return output
