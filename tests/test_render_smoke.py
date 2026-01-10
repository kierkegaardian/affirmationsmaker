import json
import tempfile
import unittest
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf

from affirmbeat.core.project import Affirmation, MusicConfig, Project, TTSConfig
from affirmbeat.render.renderer import render_project


def _write_project(path: Path, project: Project) -> Path:
    path.write_text(json.dumps(project.model_dump(), indent=2), encoding="utf-8")
    return path


class RenderSmokeTests(unittest.TestCase):
    def test_render_placeholder_music(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = Project(
                project_id=str(uuid.uuid4()),
                duration_sec=1,
                affirmations=[Affirmation(id="a1", text="I am calm.")],
                tts=TTSConfig(provider="dummy"),
                music=MusicConfig(
                    provider="placeholder",
                    prompt="",
                    chunk_sec=1,
                    crossfade_ms=0,
                ),
            )
            project.binaural.enabled = False
            project_path = _write_project(root / "project.json", project)
            output_dir = render_project(project_path)
            self.assertTrue((output_dir / "final.wav").exists())
            self.assertTrue((output_dir / "render_report.json").exists())
            self.assertTrue((output_dir / "stems").exists())

    def test_render_file_music(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sample_rate = 48_000
            duration_sec = 1
            samples = np.zeros((sample_rate * duration_sec, 2), dtype=np.float32)
            music_path = root / "music.wav"
            sf.write(music_path, samples, sample_rate)

            project = Project(
                project_id=str(uuid.uuid4()),
                duration_sec=duration_sec,
                affirmations=[Affirmation(id="a1", text="I am steady.")],
                tts=TTSConfig(provider="dummy"),
                music=MusicConfig(
                    provider="file",
                    prompt=str(music_path),
                    build_mode="single",
                    chunk_sec=duration_sec,
                    crossfade_ms=0,
                ),
            )
            project.binaural.enabled = False
            project_path = _write_project(root / "project.json", project)
            output_dir = render_project(project_path)
            self.assertTrue((output_dir / "final.wav").exists())
