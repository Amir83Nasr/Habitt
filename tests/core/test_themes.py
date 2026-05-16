"""Tests for theme management."""

import json

from habitt.core.config import CONFIG_FILE
from habitt.core.themes import (
    CUSTOM_THEMES_DIR,
    DEFAULT_THEME,
    PRESETS,
    _validate_theme,
    get_active_theme,
    get_all_themes,
    load_custom_themes,
    save_theme,
)


def test_presets_contain_default():
    assert DEFAULT_THEME in PRESETS


def test_get_active_theme_default(temp_data_dir, monkeypatch):
    # Ensure no config file
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    theme = get_active_theme()
    assert theme == PRESETS[DEFAULT_THEME]


def test_save_and_get_theme(temp_data_dir, monkeypatch):
    save_theme("forest")
    theme = get_active_theme()
    assert theme == PRESETS["forest"]
    # Config file should have theme = forest
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    assert cfg["theme"] == "forest"


def test_save_invalid_theme_raises():
    try:
        save_theme("nonexistent")
    except ValueError:
        pass
    else:
        raise AssertionError("Should raise ValueError")


def test_validate_theme_valid():
    data = {
        "app_title": "bold red",
        "panel_border": "blue",
        "success": "green",
        "warning": "yellow",
        "info": "white",
        "dim": "dim",
        "accent": "magenta",
        "error": "red",
        "checkbox_done": "green",
        "checkbox_open": "dim white",
        "tag": "purple",
        "clock": "cyan",
    }
    result = _validate_theme(data)
    assert result == data


def test_validate_theme_missing_key():
    data = {"app_title": "bold"}
    assert _validate_theme(data) is None


def test_load_custom_themes(temp_data_dir, monkeypatch):
    custom_dir = CUSTOM_THEMES_DIR
    custom_dir.mkdir(parents=True, exist_ok=True)
    theme_file = custom_dir / "mytheme.json"
    theme_data = {
        "app_title": "bold bright_green on black",
        "panel_border": "green",
        "success": "bright_green",
        "warning": "yellow",
        "info": "green",
        "dim": "dim green",
        "accent": "dark_green",
        "error": "bold red",
        "checkbox_done": "bright_green",
        "checkbox_open": "dim green",
        "tag": "dark_green",
        "clock": "bright_green",
    }
    with open(theme_file, "w") as f:
        json.dump(theme_data, f)
    customs = load_custom_themes()
    assert "mytheme" in customs
    assert customs["mytheme"] == theme_data


def test_get_all_themes_includes_custom(temp_data_dir, monkeypatch):
    custom_dir = CUSTOM_THEMES_DIR
    custom_dir.mkdir(exist_ok=True)
    theme_file = custom_dir / "custom.json"
    theme_data = {
        "app_title": "bold red on white",
        "panel_border": "red",
        "success": "green",
        "warning": "yellow",
        "info": "white",
        "dim": "dim",
        "accent": "magenta",
        "error": "red",
        "checkbox_done": "green",
        "checkbox_open": "dim white",
        "tag": "purple",
        "clock": "cyan",
    }
    with open(theme_file, "w") as f:
        json.dump(theme_data, f)
    all = get_all_themes()
    assert "custom" in all
    assert all["custom"] == theme_data
    # still has built-in
    assert DEFAULT_THEME in all
