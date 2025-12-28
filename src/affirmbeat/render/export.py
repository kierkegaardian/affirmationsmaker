from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import soundfile as sf


def export_audio(
    output_dir: Path,
    sample_rate: int,
    master: object,
    stems: dict[str, object],
    report: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    master_path = output_dir / "final.wav"
    sf.write(master_path, master, sample_rate)
    stems_dir = output_dir / "stems"
    stems_dir.mkdir(exist_ok=True)
    for name, audio in stems.items():
        sf.write(stems_dir / f"{name}.wav", audio, sample_rate)
    report_path = output_dir / "render_report.json"
    report_path.write_text(json.dumps(report, indent=2))
