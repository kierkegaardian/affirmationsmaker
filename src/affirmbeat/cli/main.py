from __future__ import annotations

import json
from pathlib import Path
import uuid

import typer

from affirmbeat.core.project import Affirmation, Project
from affirmbeat.render.renderer import render_project

app = typer.Typer(help="AffirmBeat Studio CLI")


def _default_project() -> Project:
    return Project(
        project_id=str(uuid.uuid4()),
        sample_rate=48_000,
        duration_sec=600,
        affirmations=[
            Affirmation(
                id="a1",
                text="I do what I say I will do.",
                tags=["discipline"],
            )
        ],
    )


@app.command()
def init(project_path: Path) -> None:
    """Create a starter project.json."""
    project_path.parent.mkdir(parents=True, exist_ok=True)
    project = _default_project()
    project_path.write_text(json.dumps(project.model_dump(), indent=2))
    typer.echo(f"Created {project_path}")


@app.command("add-affirmation")
def add_affirmation(project_path: Path, text: str, tag: list[str] = typer.Option(None, "--tag")) -> None:
    """Add an affirmation line."""
    data = json.loads(project_path.read_text())
    project = Project.model_validate(data)
    new_id = f"a{len(project.affirmations) + 1}"
    project.affirmations.append(Affirmation(id=new_id, text=text, tags=tag or []))
    project_path.write_text(json.dumps(project.model_dump(), indent=2))
    typer.echo(f"Added {new_id} to {project_path}")


@app.command()
def render(project_path: Path) -> None:
    """Render project to WAV outputs."""
    output = render_project(project_path)
    typer.echo(f"Rendered to {output}")
