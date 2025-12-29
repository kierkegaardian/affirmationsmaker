from __future__ import annotations

import json
import re
import textwrap
from typing import Any

from affirmbeat.providers.llm_ollama import OllamaClient


def _build_prompt(prompt: str, num_tracks: int, lines_per_track: int) -> str:
    return textwrap.dedent(
        f"""
        You are writing short affirmation lines for a multi-track audio session.

        Requirements:
        - Output JSON only (no markdown, no commentary).
        - JSON schema: {{"tracks": [{{"name": "Track 1", "lines": ["..."]}}, ...]}}
        - Create exactly {num_tracks} tracks.
        - Each track should have {lines_per_track} short lines.
        - Use present tense, positive phrasing.

        User request:
        {prompt}
        """
    ).strip()


def _extract_json(text: str) -> Any | None:
    text = text.strip()
    if not text:
        return None
    candidates: list[str] = []
    if "{" in text and "}" in text:
        candidates.append(text[text.find("{") : text.rfind("}") + 1])
    if "[" in text and "]" in text:
        candidates.append(text[text.find("[") : text.rfind("]") + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _normalize_lines(lines: list[str]) -> list[str]:
    cleaned = [line.strip() for line in lines if line and line.strip()]
    return cleaned


def _parse_tracks_from_json(
    data: Any,
    num_tracks: int,
    lines_per_track: int,
) -> list[list[str]]:
    tracks: list[list[str]] = []
    if isinstance(data, dict) and "tracks" in data:
        data = data["tracks"]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "lines" in item:
                lines = _normalize_lines([str(x) for x in item.get("lines", [])])
            elif isinstance(item, list):
                lines = _normalize_lines([str(x) for x in item])
            else:
                lines = _normalize_lines([str(item)])
            tracks.append(lines[:lines_per_track] if lines_per_track else lines)
    while len(tracks) < num_tracks:
        tracks.append([])
    return tracks[:num_tracks]


def _parse_tracks_fallback(
    text: str,
    num_tracks: int,
    lines_per_track: int,
) -> list[list[str]]:
    sections = re.split(r"(?i)\btrack\s*\d+\s*[:\-]", text)
    if len(sections) > 1:
        sections = [s for s in sections if s.strip()]
        tracks = [
            _normalize_lines(section.splitlines())[:lines_per_track]
            for section in sections
        ]
        while len(tracks) < num_tracks:
            tracks.append([])
        return tracks[:num_tracks]
    lines = _normalize_lines(text.splitlines())
    if not lines:
        return [[] for _ in range(num_tracks)]
    tracks = [[] for _ in range(num_tracks)]
    for idx, line in enumerate(lines):
        tracks[idx % num_tracks].append(line)
    if lines_per_track:
        tracks = [track[:lines_per_track] for track in tracks]
    return tracks


def generate_tracks(
    prompt: str,
    num_tracks: int,
    lines_per_track: int,
    provider: str = "ollama",
    model: str = "llama3.1:8b",
    host: str | None = None,
) -> tuple[list[list[str]], str]:
    if provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {provider}")
    client = OllamaClient(model=model, host=host)
    full_prompt = _build_prompt(prompt, num_tracks, lines_per_track)
    response = client.generate(full_prompt)
    data = _extract_json(response)
    if data is not None:
        tracks = _parse_tracks_from_json(data, num_tracks, lines_per_track)
    else:
        tracks = _parse_tracks_fallback(response, num_tracks, lines_per_track)
    return tracks, response
