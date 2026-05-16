"""Tests for focus config."""

from pathlib import Path

from habitt.core.focus_config import (
    DEFAULT_FOCUS_CONFIG,
    load_focus_config,
    resolve_music_path,
    save_focus_config,
)


def test_default_config(temp_data_dir):
    config = load_focus_config()
    assert config == DEFAULT_FOCUS_CONFIG


def test_save_and_load(temp_data_dir):
    config = load_focus_config()
    config["duration"] = 45
    config["music_enabled"] = True
    config["music_source"] = "custom:/tmp/song.mp3"
    save_focus_config(config)
    loaded = load_focus_config()
    assert loaded["duration"] == 45
    assert loaded["music_enabled"] == True


def test_resolve_music_path_none():
    config = {"music_enabled": False, "music_source": "none"}
    assert resolve_music_path(config) == ""


def test_resolve_custom_path():
    config = {"music_enabled": True, "music_source": "custom:/tmp/song.mp3"}
    # file doesn't exist, should return ""
    assert resolve_music_path(config) == ""
    # create file
    Path("/tmp/song.mp3").write_text("fake")
    assert resolve_music_path(config) == "/tmp/song.mp3"
    Path("/tmp/song.mp3").unlink()
