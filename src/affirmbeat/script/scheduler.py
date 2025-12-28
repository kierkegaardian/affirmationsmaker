from __future__ import annotations

import random
from dataclasses import dataclass

from affirmbeat.core.project import Affirmation, ScriptConfig
from affirmbeat.script.overlap_presets import OverlapVariant, variants_for_mode


@dataclass(frozen=True)
class UtterancePlan:
    text: str
    variants: list[OverlapVariant]


def build_sequence(affirmations: list[Affirmation], script: ScriptConfig) -> list[Affirmation]:
    sequence = affirmations[:]
    if script.shuffle:
        rng = random.Random(script.seed)
        rng.shuffle(sequence)
    expanded: list[Affirmation] = []
    for item in sequence:
        for _ in range(max(1, script.repeat_each)):
            expanded.append(item)
    return expanded


def build_utterance_plans(
    affirmations: list[Affirmation],
    script: ScriptConfig,
) -> list[UtterancePlan]:
    sequence = build_sequence(affirmations, script)
    variants = variants_for_mode(script.mode)
    return [UtterancePlan(text=item.text, variants=variants) for item in sequence]
