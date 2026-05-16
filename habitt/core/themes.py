"""Theme definitions and management for Habitt.

Each theme is a dictionary mapping UI element names to Rich style strings.
To add a custom theme, add a new entry to PRESETS.
Rich style syntax: "bold bright_blue on purple4", "italic #ff00ff", etc.
"""

from __future__ import annotations

import json

from habitt.core.config import CONFIG_FILE

PRESETS: dict[str, dict[str, str]] = {
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
    "ocean": {
        "app_title": "bold cyan on deep_sky_blue4",
        "panel_border": "cyan",
        "success": "bright_green",
        "warning": "gold1",
        "info": "bright_cyan",
        "dim": "dim cyan",
        "accent": "deep_sky_blue1",
        "error": "bold red",
        "checkbox_done": "bright_green",
        "checkbox_open": "dim cyan",
        "tag": "deep_sky_blue1",
        "clock": "bright_cyan",
    },
    "sunset": {
        "app_title": "bold yellow on dark_orange3",
        "panel_border": "dark_orange",
        "success": "green",
        "warning": "bright_yellow",
        "info": "orange1",
        "dim": "dim yellow",
        "accent": "dark_orange3",
        "error": "bold red",
        "checkbox_done": "green",
        "checkbox_open": "dim yellow",
        "tag": "orange1",
        "clock": "bright_yellow",
    },
    "retro": {
        "app_title": "bold bright_yellow on grey15",
        "panel_border": "bright_yellow",
        "success": "bright_green",
        "warning": "yellow",
        "info": "bright_yellow",
        "dim": "dim bright_black",
        "accent": "bright_magenta",
        "error": "bold red",
        "checkbox_done": "bright_green",
        "checkbox_open": "dim bright_black",
        "tag": "bright_magenta",
        "clock": "bright_yellow",
    },
    "midnight": {
        "app_title": "bold white on dark_blue",
        "panel_border": "dark_blue",
        "success": "bright_green",
        "warning": "yellow",
        "info": "white",
        "dim": "dim white",
        "accent": "bright_blue",
        "error": "bold red",
        "checkbox_done": "bright_green",
        "checkbox_open": "dim white",
        "tag": "bright_blue",
        "clock": "white",
    },
    "lavender": {
        "app_title": "bold bright_magenta on grey15",
        "panel_border": "bright_magenta",
        "success": "green",
        "warning": "yellow",
        "info": "bright_magenta",
        "dim": "dim bright_black",
        "accent": "purple",
        "error": "bold red",
        "checkbox_done": "green",
        "checkbox_open": "dim bright_black",
        "tag": "purple",
        "clock": "bright_magenta",
    },
    "crimson": {
        "app_title": "bold bright_red on dark_red",
        "panel_border": "bright_red",
        "success": "green",
        "warning": "yellow",
        "info": "bright_red",
        "dim": "dim red",
        "accent": "dark_red",
        "error": "bold yellow",
        "checkbox_done": "green",
        "checkbox_open": "dim red",
        "tag": "dark_red",
        "clock": "bright_red",
    },
    "amber": {
        "app_title": "bold bright_yellow on dark_orange",
        "panel_border": "dark_orange",
        "success": "green",
        "warning": "bright_yellow",
        "info": "yellow",
        "dim": "dim yellow",
        "accent": "orange1",
        "error": "bold red",
        "checkbox_done": "green",
        "checkbox_open": "dim yellow",
        "tag": "orange1",
        "clock": "bright_yellow",
    },
    "teal": {
        "app_title": "bold bright_cyan on dark_cyan",
        "panel_border": "bright_cyan",
        "success": "green",
        "warning": "yellow",
        "info": "bright_cyan",
        "dim": "dim cyan",
        "accent": "dark_cyan",
        "error": "bold red",
        "checkbox_done": "green",
        "checkbox_open": "dim cyan",
        "tag": "dark_cyan",
        "clock": "bright_cyan",
    },
    "nord": {
        "app_title": "bold white on #4c566a",
        "panel_border": "#81a1c1",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "info": "#81a1c1",
        "dim": "dim white",
        "accent": "#b48ead",
        "error": "#bf616a",
        "checkbox_done": "#a3be8c",
        "checkbox_open": "dim white",
        "tag": "#b48ead",
        "clock": "#81a1c1",
    },
}

DEFAULT_THEME: str = "blue_purple"


def get_active_theme() -> dict[str, str]:
    """Load active theme from config file, fallback to DEFAULT_THEME."""
    theme_name = DEFAULT_THEME
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)
            name = config.get("theme")
            if name in PRESETS:
                theme_name = name
    except (json.JSONDecodeError, OSError):
        pass
    return PRESETS.get(theme_name, PRESETS[DEFAULT_THEME])


def save_theme(theme_name: str) -> None:
    """Save chosen theme to config file.

    Raises ValueError if the theme name is not a valid preset.
    """
    if theme_name not in PRESETS:
        raise ValueError(f"Unknown theme: {theme_name}")
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = {"theme": theme_name}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
