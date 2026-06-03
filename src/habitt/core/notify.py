"""Send messages via external bot API."""

from __future__ import annotations

from typing import Any

from habitt.core.notify_config import load_notify_config

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def send_message(text: str) -> Any:
    config = load_notify_config()
    if not config["enabled"] or not config["bot_token"] or not config["chat_id"]:
        return False
    if not REQUESTS_AVAILABLE:
        return False

    url = config["api_url"].format(token=config["bot_token"])
    payload = {"chat_id": config["chat_id"], "text": text}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except requests.RequestException:
        return False
