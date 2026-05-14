"""Simple JSON file storage for todos and activities."""

import json
from pathlib import Path
from typing import Any


def load_json(filepath: Path) -> Any:
    """Load and return data from a JSON file. Returns empty list if file missing or corrupt."""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_json(filepath: Path, data: Any) -> None:
    """Save data to a JSON file with indentation."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
