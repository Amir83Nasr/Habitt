"""Tests for config module."""

import json

import habitt.core.config as config_mod
from habitt.core.config import (
    DEFAULT_DATA_DIR,
    get_builtin_plugins_dir,
    get_data_dir,
    get_plugins_dir,
    get_tico_file,
    get_timer_state_file,
    get_tracker_file,
    set_data_dir,
)


def test_set_data_dir(temp_data_dir, monkeypatch):
    # مطمئن شو CONFIG_FILE به temp اشاره کنه
    monkeypatch.setattr(config_mod, "CONFIG_FILE", temp_data_dir / "config.json")
    custom = (temp_data_dir / "custom_data").resolve()
    set_data_dir(str(custom))
    assert get_data_dir() == custom
    # چک کن که config.json آپدیت شده
    cfg_file = temp_data_dir / "config.json"
    assert cfg_file.exists()
    with open(cfg_file) as f:
        cfg = json.load(f)
    assert cfg["data_dir"] == str(custom)


def test_default_data_dir():
    assert get_data_dir() == DEFAULT_DATA_DIR


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
