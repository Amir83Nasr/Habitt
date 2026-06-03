"""Simple JSON file storage for todos and activities.

Provides safe load and save operations that handle missing or corrupt files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from habitt.core.backup import backup_file


def save_json(filepath: Path, data: Any) -> None:
    """Save data to a JSON file with indentation.

    Args:
        filepath (Path): The path to the JSON file.
        data (Any): The data to save.
    """
    backup_file(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath: Path) -> Any:
    """Load and return data from a JSON file.

    Args:
        filepath (Path): The path to the JSON file.

    Returns:
        Any: The loaded JSON data, or an empty list if loading fails.
    """
    if not filepath.exists():
        return []
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
