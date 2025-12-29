from __future__ import annotations

import random
from dataclasses import dataclass

from affirmbeat.core.project import ScriptConfig
from affirmbeat.script.overlap_presets import OverlapVariant, variants_for_mode


@dataclass(frozen=True)
class UtterancePlan:
    text: str
    variants: list[OverlapVariant]


def build_sequence_texts(texts: list[str], script: ScriptConfig) -> list[str]:
    sequence = texts[:]
    if script.shuffle:
        rng = random.Random(script.seed)
        rng.shuffle(sequence)
    expanded: list[str] = []
    for item in sequence:
        for _ in range(max(1, script.repeat_each)):
            expanded.append(item)
    return expanded


def build_utterance_plans(
    texts: list[str],
    script: ScriptConfig,
) -> list[UtterancePlan]:
    sequence = build_sequence_texts(texts, script)
    variants = variants_for_mode(script.mode)
    return [UtterancePlan(text=text, variants=variants) for text in sequence]
