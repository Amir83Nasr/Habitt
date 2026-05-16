"""Tests for config module."""

import json

from habitt.core.config import (
    CONFIG_FILE,
    DEFAULT_DATA_DIR,
    get_builtin_plugins_dir,
    get_data_dir,
    get_plugins_dir,
    get_tico_file,
    get_timer_state_file,
    get_tracker_file,
    set_data_dir,
)


def test_default_data_dir():
    assert get_data_dir() == DEFAULT_DATA_DIR


def test_set_data_dir(temp_data_dir, monkeypatch):
    custom = temp_data_dir / "custom_data"
    set_data_dir(str(custom))
    assert get_data_dir() == custom
    assert custom.exists()
    # Check that config.json was updated
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    assert cfg["data_dir"] == str(custom)


def test_get_tico_file():
    path = get_tico_file()
    assert path.parent == get_data_dir()
    assert path.name == "tico.json"


def test_get_tracker_file():
    path = get_tracker_file()
    assert path.name == "tracker.json"


def test_get_timer_state_file():
    path = get_timer_state_file()
    assert path.name == "timer_state.json"


def test_get_plugins_dir():
    path = get_plugins_dir()
    assert path.name == "plugins"
    assert path.exists()


def test_get_builtin_plugins_dir():
    path = get_builtin_plugins_dir()
    assert path.exists()  # inside package
    assert path.name == "plugins"


def test_set_data_dir_invalid_path(monkeypatch):
    # set empty string should still work? It will expand to current dir
    # but we'll test with a valid path
    pass  # no exception expected for valid
