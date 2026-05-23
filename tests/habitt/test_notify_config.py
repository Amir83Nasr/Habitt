"""Tests for notify config."""

from habitt.core.notify_config import (
    DEFAULT_NOTIFY_CONFIG,
    load_notify_config,
    save_notify_config,
)


def test_default_notify_config(temp_data_dir):
    from habitt.core.notify_config import NOTIFY_CONFIG_FILE

    if NOTIFY_CONFIG_FILE.exists():
        NOTIFY_CONFIG_FILE.unlink()
    config = load_notify_config()
    assert config == DEFAULT_NOTIFY_CONFIG


def test_save_and_load_notify_config(temp_data_dir):
    config = load_notify_config()
    config["enabled"] = True
    config["bot_token"] = "test"
    save_notify_config(config)
    loaded = load_notify_config()
    assert loaded["enabled"]
    assert loaded["bot_token"] == "test"
