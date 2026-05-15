"""Central configuration for paths and constants."""

import json
from pathlib import Path

APP_NAME = "habitt"
DEFAULT_DATA_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = DEFAULT_DATA_DIR / "config.json"

# Make sure default dir exists for config
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """Load config.json as dict, or return empty dict."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
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
    return get_data_dir() / "tico.json"


def get_tracker_file() -> Path:
    return get_data_dir() / "tracker.json"


def get_timer_state_file() -> Path:
    return get_data_dir() / "timer_state.json"


def set_data_dir(path_str: str) -> None:
    """Save a new data directory path to config.json."""
    new_path = Path(path_str).expanduser().resolve()
    # Validate that we can create it
    new_path.mkdir(parents=True, exist_ok=True)
    config = _load_config()
    config["data_dir"] = str(new_path)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
