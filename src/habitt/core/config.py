"""Central configuration for paths and constants."""

from pathlib import Path

APP_NAME = "habitt"
DATA_DIR = Path.home() / f".{APP_NAME}"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TICO_FILE = DATA_DIR / "tico.json"
TRACKER_FILE = DATA_DIR / "tracker.json"
CONFIG_FILE = DATA_DIR / "config.json"

TIMER_STATE_FILE = DATA_DIR / "timer_state.json"
