"""Focus mode configuration and music discovery."""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import Any

from habitt.core.config import get_data_dir

FOCUS_CONFIG_FILE = get_data_dir() / "focus_config.json"

DEFAULT_FOCUS_CONFIG: dict[str, Any] = {
    "duration": 25,
    "music_enabled": False,
    "music_source": "none",  # "none" | "builtin:<name>" | "custom:<abs_path>"
}


def load_focus_config() -> dict[str, Any]:
    if FOCUS_CONFIG_FILE.exists():
        try:
            with open(FOCUS_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for key, val in DEFAULT_FOCUS_CONFIG.items():
                if key not in data:
                    data[key] = val
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_FOCUS_CONFIG)


def save_focus_config(config: dict[str, Any]) -> None:
    FOCUS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FOCUS_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_user_music_dir() -> Path:
    """Return the user's focus music directory."""
    music_dir = get_data_dir() / "focus_music"
    music_dir.mkdir(parents=True, exist_ok=True)
    return music_dir


def list_user_music() -> list[Path]:
    """Return list of audio files in the user's music directory."""
    music_dir = get_user_music_dir()
    files = []
    for ext in (".mp3", ".wav", ".m4a", ".flac", ".ogg"):
        files.extend(sorted(music_dir.glob(f"*{ext}")))
    return files


def list_builtin_music() -> list[str]:
    """Return list of built-in music filenames (without extension)."""
    try:
        music_dir = importlib.resources.files("habitt") / "assets" / "music"
        if music_dir.is_dir():
            return sorted(
                [f.name for f in music_dir.iterdir() if f.suffix in (".mp3", ".wav")]
            )
    except Exception:
        pass
    return []


def get_builtin_music_path(name: str) -> str:
    """Return absolute path to a built-in music file."""
    try:
        ref = importlib.resources.files("habitt") / "assets" / "music" / name
        if ref.is_file():
            return str(ref)
    except Exception:
        pass
    return ""


def resolve_music_path(config: dict[str, Any]) -> str:
    """Return the resolved music file path based on config."""
    if not config.get("music_enabled", False):
        return ""
    source = config.get("music_source", "none")
    if source == "none":
        return ""
    elif source.startswith("builtin:"):
        name = source.split(":", 1)[1]
        return get_builtin_music_path(name)
    elif source.startswith("custom:"):
        path = source.split(":", 1)[1]
        if Path(path).is_file():
            return path
    return ""
