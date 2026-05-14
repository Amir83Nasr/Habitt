"""
Theme definitions and management for Habitt.

This module provides a set of predefined color themes and a function
to load the user's active theme from the configuration file.

Each theme is a dictionary that maps UI element names to Rich style strings.
You can customize colors by editing the dictionaries below or by creating
a new preset and adding it to PRESETS.

Rich style strings can include:
- color names: "red", "blue", "green", etc.
- bright variants: "bright_blue", "bright_green"
- modifiers: "bold", "dim", "italic", "underline", "reverse"
- background colors: "on purple4", "on grey23"
- Combine them: "bold bright_blue on purple4"
- Hex colors: "#ff00ff"
"""

import json
from pathlib import Path
from typing import Dict

from habitt.core.config import CONFIG_FILE

# ----------------------------------------------------------------------
# Preset themes
# ----------------------------------------------------------------------

PRESETS: Dict[str, Dict[str, str]] = {
    "blue_purple": {
        "app_title": "bold bright_blue on purple4",
        "panel_border": "purple",
        "success": "green",
        "warning": "yellow",
        "info": "bright_blue",
        "dim": "dim white",
        "accent": "magenta",
        "error": "bold red",
        "checkbox_done": "green",
        "checkbox_open": "dim white",
        "tag": "magenta",
        "clock": "bright_blue",
    },
    "forest": {
        "app_title": "bold bright_green on dark_green",
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
    },
    "mono": {
        "app_title": "bold white on grey23",
        "panel_border": "white",
        "success": "bold white",
        "warning": "bold yellow",
        "info": "white",
        "dim": "dim white",
        "accent": "bold white",
        "error": "bold red",
        "checkbox_done": "bold white",
        "checkbox_open": "dim white",
        "tag": "italic white",
        "clock": "white",
    },
}

DEFAULT_THEME = "blue_purple"


def get_active_theme() -> Dict[str, str]:
    """
    Return the currently active theme dictionary.

    Loads the theme name from CONFIG_FILE (if it exists and is valid),
    then returns the corresponding preset. Falls back to DEFAULT_THEME
    if anything goes wrong.
    """
    theme_name = DEFAULT_THEME
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            name = config.get("theme")
            if name in PRESETS:
                theme_name = name
    except (json.JSONDecodeError, OSError):
        pass

    return PRESETS.get(theme_name, PRESETS[DEFAULT_THEME])


def save_theme(theme_name: str) -> None:
    """
    Save the given theme name to the configuration file.

    Raises ValueError if the theme name is not a valid preset.
    """
    if theme_name not in PRESETS:
        raise ValueError(f"Unknown theme: {theme_name}")
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = {"theme": theme_name}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
