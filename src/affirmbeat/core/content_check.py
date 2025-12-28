from __future__ import annotations

import re

from affirmbeat.core.project import Affirmation

_NEGATION_PATTERNS = [
    r"\bnot\b",
    r"\bnever\b",
    r"\bno\b",
    r"\bdon't\b",
    r"\bcan't\b",
    r"\bwon't\b",
    r"\bshouldn't\b",
    r"\bavoid\b",
]

_NEGATIVE_WORD_PATTERNS = [
    r"\bhate\b",
    r"\bworthless\b",
    r"\bstupid\b",
    r"\bugly\b",
    r"\bfailure\b",
    r"\bfail\b",
    r"\bbad\b",
    r"\bdepressed\b",
]


def find_content_warnings(affirmations: list[Affirmation]) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    for affirmation in affirmations:
        text = affirmation.text
        lowered = text.lower()
        flags: list[str] = []
        if any(re.search(pattern, lowered) for pattern in _NEGATION_PATTERNS):
            flags.append("negation")
        if any(re.search(pattern, lowered) for pattern in _NEGATIVE_WORD_PATTERNS):
            flags.append("negative_word")
        if flags:
            warnings.append(
                {
                    "affirmation_id": affirmation.id,
                    "text": text,
                    "flags": flags,
                }
            )
    return warnings
