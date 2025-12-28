from __future__ import annotations

from pathlib import Path
import os


def cache_dir(project_path: Path) -> Path:
    override = os.getenv("AFFIRMBEAT_CACHE_DIR")
    if override:
        return Path(override)
    return project_path.parent / "cache"


def output_dir(project_path: Path) -> Path:
    return project_path.parent / "output"
