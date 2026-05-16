"""Central configuration for paths and constants.

Provides functions to get and set data and plugin directories,
and manages the configuration file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_NAME: str = "habitt"
DEFAULT_DATA_DIR: Path = Path.home() / f".{APP_NAME}"
CONFIG_FILE: Path = DEFAULT_DATA_DIR / "config.json"

DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_data_dir() -> Path:
    """Return the current data directory (default or custom)."""
    config = _load_config()
    custom = config.get("data_dir")
    if custom:
        custom_path = Path(custom).expanduser().resolve()
        custom_path.mkdir(parents=True, exist_ok=True)
        return custom_path
    return DEFAULT_DATA_DIR


def get_tico_file() -> Path:
    """Return path to the tico JSON file."""
    return get_data_dir() / "tico.json"


def get_tracker_file() -> Path:
    """Return path to the tracker JSON file."""
    return get_data_dir() / "tracker.json"


def get_timer_state_file() -> Path:
    """Return path to the timer state JSON file."""
    return get_data_dir() / "timer_state.json"


def set_data_dir(path_str: str) -> None:
    """Save a new data directory path to config.json."""
    new_path = Path(path_str).expanduser().resolve()
    new_path.mkdir(parents=True, exist_ok=True)
    config = _load_config()
    config["data_dir"] = str(new_path)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_plugins_dir() -> Path:
    """Return the user plugins directory."""
    plugins_dir = get_data_dir() / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    return plugins_dir


def get_builtin_plugins_dir() -> Path:
    """Return the built-in plugins directory inside the package."""
    import habitt

    return Path(habitt.__file__).parent / "plugins"
