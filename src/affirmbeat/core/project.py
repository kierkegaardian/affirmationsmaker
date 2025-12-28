from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Affirmation(BaseModel):
    id: str
    text: str
    tags: list[str] = Field(default_factory=list)


class ScriptConfig(BaseModel):
    mode: Literal[
        "single",
        "triple_stack",
        "lead_whisper",
        "call_response",
    ] = "single"
    repeat_each: int = 1
    gap_ms: int = 400
    shuffle: bool = False
    seed: int = 0


class TTSConfig(BaseModel):
    provider: str = "dummy"
    voice: str | None = None
    rate: float = 1.0
    model_path: str | None = None


class MusicConfig(BaseModel):
    provider: str = "placeholder"
    prompt: str = ""
    seed: int = 0
    build_mode: str = "loop_crossfade"
    chunk_sec: int = 30
    crossfade_ms: int = 1500
    bpm: int | None = None
    model_id: str | None = None
    device: str | None = None
    steps: int = 100
    guidance_scale: float | None = None
    sigma_min: float | None = None
    sigma_max: float | None = None
    sampler: str | None = None


class BinauralConfig(BaseModel):
    enabled: bool = True
    carrier_hz: float = 220.0
    beat_hz: float = 6.0
    gain_db: float = -30.0
    fade_in_ms: int = 10_000
    fade_out_ms: int = 10_000


class MixConfig(BaseModel):
    master_peak_db: float = -1.0
    target_lufs: float | None = None


class Project(BaseModel):
    project_id: str
    sample_rate: int = 48_000
    duration_sec: int = 1_800
    affirmations: list[Affirmation] = Field(default_factory=list)
    script: ScriptConfig = Field(default_factory=ScriptConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    music: MusicConfig = Field(default_factory=MusicConfig)
    binaural: BinauralConfig = Field(default_factory=BinauralConfig)
    mix: MixConfig = Field(default_factory=MixConfig)
