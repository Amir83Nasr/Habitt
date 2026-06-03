"""Notification configuration for Habitt."""

from __future__ import annotations

import json
from typing import Any

from habitt.core.config import get_data_dir

NOTIFY_CONFIG_FILE = get_data_dir() / "notify_config.json"

DEFAULT_NOTIFY_CONFIG: dict[str, Any] = {
    "enabled": False,
    "bot_token": "",
    "chat_id": "",
    "api_url": "https://uniom.ir/bot{token}/sendMessage",
}


def load_notify_config() -> dict[str, Any]:
    """Load notification settings, falling back to defaults."""
    if NOTIFY_CONFIG_FILE.exists():
        try:
            with open(NOTIFY_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for key, value in DEFAULT_NOTIFY_CONFIG.items():
                    if key not in data:
                        data[key] = value
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_NOTIFY_CONFIG)


def save_notify_config(config: dict[str, Any]) -> None:
    """Persist notification settings."""
    NOTIFY_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTIFY_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
