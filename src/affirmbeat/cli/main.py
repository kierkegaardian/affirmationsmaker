from __future__ import annotations

import json
from pathlib import Path
import uuid

import typer

from affirmbeat.core.project import Affirmation, Project, TextGenConfig, VoiceTrack
from affirmbeat.render.renderer import render_project
from affirmbeat.script.textgen import generate_tracks

app = typer.Typer(help="AffirmBeat Studio CLI")
SUPPORTED_MODES = ("single", "triple_stack", "lead_whisper", "call_response")


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


def _prompt_lines(label: str) -> list[str]:
    typer.echo(f"Enter lines for {label}. Submit a blank line to finish.")
    lines: list[str] = []
    while True:
        line = typer.prompt("Line", default="", show_default=False, prompt_required=False)
        if not line:
            break
        lines.append(line)
    return lines


def _normalize_mode(mode: str, label: str) -> str:
    normalized = mode.strip()
    lowered = normalized.lower()
    if lowered in SUPPORTED_MODES:
        return lowered
    raise typer.BadParameter(
        f"{label} must be one of: {', '.join(SUPPORTED_MODES)}."
    )


def _prompt_voice_tracks(num_tracks: int, default_mode: str) -> list[VoiceTrack]:
    tracks: list[VoiceTrack] = []
    for idx in range(num_tracks):
        default_id = f"track{idx + 1}"
        track_id = typer.prompt(f"Track {idx + 1} id", default=default_id)
        voice = typer.prompt(
            f"Voice for {track_id} (blank = default)",
            default="",
            show_default=False,
            prompt_required=False,
        )
        gain_db = typer.prompt(f"{track_id} gain dB", default=0.0, type=float)
        pan = typer.prompt(f"{track_id} pan (-1 to 1)", default=0.0, type=float)
        start_offset_ms = typer.prompt(f"{track_id} start offset ms", default=0, type=int)
        mode_override = typer.prompt(
            f"{track_id} overlap mode (blank = {default_mode})",
            default="",
            show_default=False,
            prompt_required=False,
        )
        if mode_override.strip():
            mode_override = _normalize_mode(
                mode_override,
                f"{track_id} overlap mode",
            )
        tracks.append(
            VoiceTrack(
                id=track_id,
                voice=voice or None,
                gain_db=gain_db,
                pan=pan,
                start_offset_ms=start_offset_ms,
                mode=mode_override or None,
            )
        )
    return tracks


@app.command("tui")
def tui(project_path: Path = Path("projects/new_project.json")) -> None:
    """Interactive text UI wizard to build a project.json."""
    project_id = str(uuid.uuid4())
    sample_rate = typer.prompt("Sample rate", default=48_000, type=int)
    duration_min = typer.prompt("Session length (minutes)", default=10.0, type=float)
    duration_sec = int(duration_min * 60)

    script_mode = typer.prompt(
        "Overlap mode",
        default="single",
    )
    script_mode = _normalize_mode(script_mode, "Overlap mode")
    repeat_each = typer.prompt("Repeat each line", default=1, type=int)
    gap_ms = typer.prompt("Gap between lines (ms)", default=400, type=int)
    shuffle = typer.confirm("Shuffle lines", default=False)

    tts_provider = typer.prompt(
        "TTS provider (dummy/espeak/piper1)",
        default="dummy",
    )
    tts_voice = typer.prompt(
        "Default TTS voice (blank = provider default)",
        default="",
        show_default=False,
        prompt_required=False,
    )
    tts_rate = typer.prompt("TTS rate", default=1.0, type=float)
    tts_model_path = None
    if tts_provider == "piper1":
        tts_model_path = typer.prompt("Piper model path", default="")

    num_tracks = typer.prompt("Number of lyric tracks", default=1, type=int)
    if num_tracks < 1:
        typer.echo("Number of lyric tracks must be >= 1. Using 1.")
        num_tracks = 1
    voice_tracks = _prompt_voice_tracks(num_tracks, script_mode)

    use_llm = typer.confirm("Generate track lines with LLM", default=False)
    textgen: TextGenConfig | None = None
    if use_llm:
        llm_provider = typer.prompt("LLM provider", default="ollama")
        llm_model = typer.prompt("LLM model", default="llama3.1:8b")
        llm_prompt = typer.prompt("LLM prompt/request", default="Write calm, positive affirmations.")
        lines_per_track = typer.prompt("Lines per track", default=6, type=int)
        llm_host = typer.prompt(
            "LLM host override (blank = OLLAMA_HOST)",
            default="",
            show_default=False,
            prompt_required=False,
        )
        try:
            tracks_lines, _ = generate_tracks(
                prompt=llm_prompt,
                num_tracks=num_tracks,
                lines_per_track=lines_per_track,
                provider=llm_provider,
                model=llm_model,
                host=llm_host or None,
            )
            for idx, track in enumerate(voice_tracks):
                track.lines = tracks_lines[idx] if idx < len(tracks_lines) else []
            textgen = TextGenConfig(
                provider=llm_provider,
                model=llm_model,
                prompt=llm_prompt,
                num_tracks=num_tracks,
                lines_per_track=lines_per_track,
                host=llm_host or None,
            )
        except Exception as exc:
            typer.echo(f"LLM generation failed: {exc}")
            use_llm = False

    if not use_llm:
        for track in voice_tracks:
            track.lines = _prompt_lines(track.id)

    music_provider = typer.prompt(
        "Music provider (placeholder/stable_audio_open)",
        default="placeholder",
    )
    music_prompt = typer.prompt(
        "Music prompt/style",
        default="downtempo ambient beat, no vocals, warm pads",
    )
    music_seed = typer.prompt("Music seed", default=123, type=int)
    chunk_sec = typer.prompt("Music chunk seconds", default=30, type=int)
    crossfade_ms = typer.prompt("Music crossfade (ms)", default=1500, type=int)
    model_id = None
    if music_provider == "stable_audio_open":
        model_id = typer.prompt(
            "Stable Audio model id",
            default="stabilityai/stable-audio-open-1.0",
        )

    binaural_enabled = typer.confirm("Enable binaural beats", default=True)
    carrier_hz = typer.prompt("Binaural carrier Hz", default=220.0, type=float)
    beat_hz = typer.prompt("Binaural beat Hz", default=6.0, type=float)
    binaural_gain = typer.prompt("Binaural gain (dB)", default=-30.0, type=float)
    fade_in_ms = typer.prompt("Binaural fade in (ms)", default=10_000, type=int)
    fade_out_ms = typer.prompt("Binaural fade out (ms)", default=10_000, type=int)

    master_peak = typer.prompt("Master peak dB", default=-1.0, type=float)
    target_lufs = typer.prompt(
        "Target LUFS (blank = disabled)",
        default="",
        show_default=False,
        prompt_required=False,
    )

    project = Project(
        project_id=project_id,
        sample_rate=sample_rate,
        duration_sec=duration_sec,
        affirmations=[],
        voice_tracks=voice_tracks,
        script={
            "mode": script_mode,
            "repeat_each": repeat_each,
            "gap_ms": gap_ms,
            "shuffle": shuffle,
        },
        tts={
            "provider": tts_provider,
            "voice": tts_voice or None,
            "rate": tts_rate,
            "model_path": tts_model_path or None,
        },
        music={
            "provider": music_provider,
            "prompt": music_prompt,
            "seed": music_seed,
            "build_mode": "loop_crossfade",
            "chunk_sec": chunk_sec,
            "crossfade_ms": crossfade_ms,
            "model_id": model_id,
        },
        binaural={
            "enabled": binaural_enabled,
            "carrier_hz": carrier_hz,
            "beat_hz": beat_hz,
            "gain_db": binaural_gain,
            "fade_in_ms": fade_in_ms,
            "fade_out_ms": fade_out_ms,
        },
        mix={
            "master_peak_db": master_peak,
            "target_lufs": float(target_lufs) if str(target_lufs).strip() else None,
        },
        textgen=textgen,
    )

    project_path.parent.mkdir(parents=True, exist_ok=True)
    project_path.write_text(json.dumps(project.model_dump(), indent=2))
    typer.echo(f"Created {project_path}")

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


@app.command("generate-tracks")
def generate_tracks_cmd(
    project_path: Path,
    prompt: str,
    provider: str = "ollama",
    model: str = "llama3.1:8b",
    num_tracks: int | None = None,
    lines_per_track: int = 6,
    host: str | None = None,
) -> None:
    """Generate voice track lines via LLM and write back to project.json."""
    data = json.loads(project_path.read_text())
    project = Project.model_validate(data)
    track_count = num_tracks or len(project.voice_tracks) or 1
    while len(project.voice_tracks) < track_count:
        project.voice_tracks.append(VoiceTrack(id=f"track{len(project.voice_tracks) + 1}"))
    tracks_lines, _ = generate_tracks(
        prompt=prompt,
        num_tracks=track_count,
        lines_per_track=lines_per_track,
        provider=provider,
        model=model,
        host=host,
    )
    for idx, track in enumerate(project.voice_tracks[:track_count]):
        track.lines = tracks_lines[idx] if idx < len(tracks_lines) else []
    project.textgen = TextGenConfig(
        provider=provider,
        model=model,
        prompt=prompt,
        num_tracks=track_count,
        lines_per_track=lines_per_track,
        host=host,
    )
    project_path.write_text(json.dumps(project.model_dump(), indent=2))
    typer.echo(f"Generated {track_count} track(s) in {project_path}")


@app.command()
def render(project_path: Path) -> None:
    """Render project to WAV outputs."""
    output = render_project(project_path)
    typer.echo(f"Rendered to {output}")
