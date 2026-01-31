from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, model_validator


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
    repeat_each: int = Field(default=1, ge=1)
    gap_ms: int = Field(default=400, ge=0)
    shuffle: bool = False
    seed: int = 0


class TTSConfig(BaseModel):
    provider: str = "dummy"
    voice: str | None = None
    rate: float = 1.0
    model_path: str | None = None


class VoiceTrack(BaseModel):
    id: str
    voice: str | None = None
    lines: list[str] = Field(default_factory=list)
    gain_db: float = 0.0
    pan: float = 0.0
    start_offset_ms: int = 0
    mode: str | None = None


class TextGenConfig(BaseModel):
    provider: str = "ollama"
    model: str = "llama3.1:8b"
    prompt: str = ""
    num_tracks: int = 1
    lines_per_track: int = 6
    host: str | None = None


class MusicConfig(BaseModel):
    provider: str = "placeholder"
    prompt: str = ""
    seed: int = 0
    build_mode: str = "loop_crossfade"
    chunk_sec: int = Field(default=30, gt=0)
    crossfade_ms: int = Field(default=1500, ge=0)
    bpm: int | None = None
    gain_db: float = -16.0
    model_id: str | None = None
    device: str | None = None
    steps: int = 100
    guidance_scale: float | None = None
    sigma_min: float | None = None
    sigma_max: float | None = None
    sampler: str | None = None

    @model_validator(mode="after")
    def validate_crossfade_chunk(self) -> "MusicConfig":
        if self.build_mode == "loop_crossfade":
            max_crossfade_ms = self.chunk_sec * 1000
            if self.crossfade_ms > max_crossfade_ms:
                raise ValueError(
                    "music.crossfade_ms must be <= music.chunk_sec * 1000 when build_mode is loop_crossfade"
                )
        return self


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
    sample_rate: int = Field(default=48_000, gt=0)
    duration_sec: int = Field(default=1_800, gt=0)
    affirmations: list[Affirmation] = Field(default_factory=list)
    voice_tracks: list[VoiceTrack] = Field(default_factory=list)
    script: ScriptConfig = Field(default_factory=ScriptConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    music: MusicConfig = Field(default_factory=MusicConfig)
    binaural: BinauralConfig = Field(default_factory=BinauralConfig)
    mix: MixConfig = Field(default_factory=MixConfig)
    textgen: TextGenConfig | None = None
