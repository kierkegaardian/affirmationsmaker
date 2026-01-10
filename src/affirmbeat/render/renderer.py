from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from affirmbeat.core.hashing import hash_dict
from affirmbeat.core.paths import cache_dir, output_dir
from affirmbeat.core.project import Project
from affirmbeat.core.content_check import (
    find_content_warnings,
    find_content_warnings_for_texts,
)
from affirmbeat.dsp.binaural import generate_binaural
from affirmbeat.providers.music_file import FileMusicProvider
from affirmbeat.providers.music_placeholder import PlaceholderMusicProvider
from affirmbeat.providers.music_stable_audio import StableAudioOpenProvider
from affirmbeat.providers.tts_dummy import DummyTTSProvider
from affirmbeat.providers.tts_espeak import EspeakTTSProvider
from affirmbeat.providers.tts_piper1 import PiperTTSProvider
from affirmbeat.render.export import export_audio
from affirmbeat.render.mixer import mix_tracks
from affirmbeat.render.music_bed import build_music_bed
from affirmbeat.render.timeline import Clip, place_clips
from affirmbeat.script.scheduler import build_utterance_plans


def _load_project(path: Path) -> Project:
    data = json.loads(path.read_text())
    return Project.model_validate(data)


def _tts_provider(project: Project):
    if project.tts.provider == "piper1":
        return PiperTTSProvider(project.sample_rate, project.tts.model_path)
    if project.tts.provider == "espeak":
        return EspeakTTSProvider(project.sample_rate)
    return DummyTTSProvider(project.sample_rate)


def _music_provider(project: Project):
    if project.music.provider == "file":
        return FileMusicProvider(project.sample_rate)
    if project.music.provider == "stable_audio_open":
        model_id = project.music.model_id or "stabilityai/stable-audio-open-1.0"
        return StableAudioOpenProvider(
            project.sample_rate,
            model_id=model_id,
            device=project.music.device,
            steps=project.music.steps,
            guidance_scale=project.music.guidance_scale,
            sigma_min=project.music.sigma_min,
            sigma_max=project.music.sigma_max,
            sampler=project.music.sampler,
        )
    if project.music.provider == "placeholder":
        return PlaceholderMusicProvider(project.sample_rate)
    warnings.warn(
        f"Unknown music provider {project.music.provider!r}; using placeholder noise.",
        RuntimeWarning,
    )
    return PlaceholderMusicProvider(project.sample_rate)


def _tts_cache_key(project: Project, text: str, voice: str | None) -> str:
    return hash_dict(
        {
            "provider": project.tts.provider,
            "voice": voice,
            "rate": project.tts.rate,
            "model_path": project.tts.model_path,
            "text": text,
            "sample_rate": project.sample_rate,
        }
    )


def _load_or_synthesize_tts(
    project: Project,
    project_path: Path,
    provider,
    text: str,
    voice: str | None,
    report: dict[str, Any],
) -> np.ndarray:
    cache_root = cache_dir(project_path) / "tts"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_key = _tts_cache_key(project, text, voice)
    cache_path = cache_root / f"{cache_key}.wav"
    if cache_path.exists():
        audio, _ = sf.read(cache_path, dtype="float32")
        report["tts_cached"].append(cache_path.name)
        return audio
    audio = provider.synthesize(
        text,
        voice,
        {
            "rate": project.tts.rate,
            "model_path": project.tts.model_path,
        },
    )
    sf.write(cache_path, audio, project.sample_rate)
    report["tts_generated"].append(cache_path.name)
    return audio


def render_project(project_path: Path) -> Path:
    project = _load_project(project_path)
    content_warnings = find_content_warnings(project.affirmations)
    if project.voice_tracks:
        for track in project.voice_tracks:
            content_warnings.extend(
                find_content_warnings_for_texts(track.lines, track_id=track.id)
            )
    report: dict[str, Any] = {
        "project_id": project.project_id,
        "tts_cached": [],
        "tts_generated": [],
        "music_cached": [],
        "music_generated": [],
        "seeds": {
            "script_seed": project.script.seed,
            "music_seed": project.music.seed,
        },
        "providers": {
            "tts": project.tts.provider,
            "music": project.music.provider,
        },
        "content_warnings": content_warnings,
    }
    if project.textgen is not None:
        report["textgen"] = project.textgen.model_dump()

    tts = _tts_provider(project)

    total_samples = int(project.duration_sec * project.sample_rate)
    allowed_modes = {"single", "triple_stack", "lead_whisper", "call_response"}
    clips: list[Clip] = []
    if project.voice_tracks:
        for track in project.voice_tracks:
            if not track.lines:
                continue
            script_cfg = project.script
            if track.mode:
                if track.mode not in allowed_modes:
                    raise ValueError(
                        f"Invalid track.mode '{track.mode}' for track '{track.id}'. "
                        f"Supported modes: {', '.join(sorted(allowed_modes))}."
                    )
                script_cfg = project.script.model_copy(
                    update={"mode": track.mode},
                    validate=True,
                )
            utterance_plans = build_utterance_plans(track.lines, script_cfg)
            current_start = int((track.start_offset_ms / 1000.0) * project.sample_rate)
            gap_samples = int((script_cfg.gap_ms / 1000.0) * project.sample_rate)
            for plan in utterance_plans:
                audio = _load_or_synthesize_tts(
                    project,
                    project_path,
                    tts,
                    plan.text,
                    track.voice or project.tts.voice,
                    report,
                )
                if audio.ndim > 1:
                    audio = audio[:, 0]
                duration_samples = audio.shape[0]
                for variant in plan.variants:
                    offset_samples = int(
                        (variant.offset_ms / 1000.0) * project.sample_rate
                    )
                    clips.append(
                        Clip(
                            audio=audio,
                            start_sample=current_start + offset_samples,
                            gain_db=variant.gain_db + track.gain_db,
                            pan=variant.pan + track.pan,
                            track=track.id,
                        )
                    )
                current_start += duration_samples + gap_samples
                if current_start >= total_samples:
                    break
    else:
        utterance_plans = build_utterance_plans(
            [item.text for item in project.affirmations],
            project.script,
        )
        current_start = 0
        gap_samples = int((project.script.gap_ms / 1000.0) * project.sample_rate)
        for plan in utterance_plans:
            audio = _load_or_synthesize_tts(
                project,
                project_path,
                tts,
                plan.text,
                project.tts.voice,
                report,
            )
            if audio.ndim > 1:
                audio = audio[:, 0]
            duration_samples = audio.shape[0]
            for variant in plan.variants:
                offset_samples = int((variant.offset_ms / 1000.0) * project.sample_rate)
                clips.append(
                    Clip(
                        audio=audio,
                        start_sample=current_start + offset_samples,
                        gain_db=variant.gain_db,
                        pan=variant.pan,
                        track=variant.track,
                    )
                )
            current_start += duration_samples + gap_samples
            if current_start >= total_samples:
                break

    music = _music_provider(project)
    music_audio = build_music_bed(project, project_path, music, report)
    clips.append(
        Clip(
            audio=music_audio,
            start_sample=0,
            gain_db=project.music.gain_db,
            pan=0.0,
            track="music",
        )
    )

    if project.binaural.enabled:
        binaural = generate_binaural(
            project.duration_sec,
            project.sample_rate,
            project.binaural.carrier_hz,
            project.binaural.beat_hz,
            project.binaural.gain_db,
            project.binaural.fade_in_ms,
            project.binaural.fade_out_ms,
        )
        clips.append(
            Clip(
                audio=binaural,
                start_sample=0,
                gain_db=0.0,
                pan=0.0,
                track="binaural",
            )
        )

    tracks = place_clips(total_samples, clips, project.sample_rate)
    master = mix_tracks(
        tracks,
        project.mix.master_peak_db,
        project.sample_rate,
        project.mix.target_lufs,
    )
    output = output_dir(project_path)
    export_audio(output, project.sample_rate, master, tracks, report)
    return output
