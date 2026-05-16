"""Automatic backup of data files."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from habitt.core.config import get_data_dir

MAX_BACKUPS = 10


def backup_file(filepath: Path) -> None:
    """Create a timestamped backup of the given file, keep last MAX_BACKUPS."""
    if not filepath.exists():
        return
    backup_dir = get_data_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(filepath, backup_path)

    # Purge old backups
    pattern = f"{filepath.stem}_*{filepath.suffix}"
    backups = sorted(
        backup_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
    )
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        oldest.unlink()
