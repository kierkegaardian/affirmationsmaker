from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class OverlapVariant:
    track: str
    pan: float
    gain_db: float
    offset_ms: int


def variants_for_mode(mode: str) -> list[OverlapVariant]:
    if mode == "triple_stack":
        return [
            OverlapVariant(track="voice", pan=-0.6, gain_db=-2.0, offset_ms=0),
            OverlapVariant(track="voice", pan=0.0, gain_db=0.0, offset_ms=60),
            OverlapVariant(track="voice", pan=0.6, gain_db=-2.0, offset_ms=120),
        ]
    if mode == "lead_whisper":
        return [
            OverlapVariant(track="voice", pan=0.0, gain_db=0.0, offset_ms=0),
            OverlapVariant(track="whisper", pan=0.2, gain_db=-10.0, offset_ms=80),
        ]
    if mode == "call_response":
        return [
            OverlapVariant(track="call", pan=-0.4, gain_db=-1.0, offset_ms=0),
            OverlapVariant(track="response", pan=0.4, gain_db=-1.0, offset_ms=400),
        ]
    return [OverlapVariant(track="voice", pan=0.0, gain_db=0.0, offset_ms=0)]
