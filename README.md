# Habitt

![Habitt Logo](assets/Tico.png)

## Terminal-based habit tracker with todo (tico) and activity logger (tracker)

Manage your daily tasks and activities entirely from the terminal.
Built with [Rich](https://github.com/Textualize/rich) for a beautiful TUI,
[Click](https://click.palletsprojects.com/) for a powerful CLI,
and [jdatetime](https://github.com/slashmili/python-jalali) for Shamsi (Jalali) calendar support.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

---

## Features

### 📋 Tico – Todo Manager

- Simple checkboxes (`[x]` / `[ ]`) like Markdown
- Tag-based organization (`#work`, `#personal`, ...)
- Arrow-key navigable menu
- Add, toggle, remove tasks by row number
- Filter by tag
- Bulk operations (toggle/remove multiple tasks at once)

### ⏱️ Tracker – Activity Logger

- Log daily activities with start/end times
- **Live timer** with pause, resume, stop
- Manual time entry with automatic date and time validation
- Daily and weekly statistics with bar charts
- Export to JSON, CSV, or beautifully formatted TXT files
- Remove activities by row number

### 🧩 Plugin System

- Built-in plugins: **Calendar** (Shamsi), **Pomodoro Timer**, **Quick Notes**
- User plugins via `~/.habitt/plugins/`
- Automatic discovery of user and built-in plugins

### 🎨 Custom Themes

- 12 built-in color themes (blue_purple, forest, ocean, sunset, nord, ...)
- Custom themes via JSON files in `~/.habitt/themes/`
- Instant preview in settings menu

### ⚙️ Settings

- Theme selection with live preview
- Change data directory
- Export all data (JSON/CSV/TXT) to Desktop
- Focus music settings (built-in or custom Lo-Fi tracks)
- Reset all data with confirmation

### 🛡️ Data Safety

- Automatic backups of data files (last 10 versions)
- JSON storage in `~/.habitt/` (no database server needed)
- Validated date/time input to prevent corruption

### ⌨️ Terminal Experience

- Arrow-key navigation in all menus
- Single-key shortcuts for quick actions
- Tab completion for CLI commands (bash/zsh)
- Beautiful Rich-based tables, panels, and progress bars

---

## Installation

### From PyPI (recommended)

```bash
pip install habitt
```

### From source (development mode)

```bash
git clone https://github.com/yourusername/habitt.git
cd habitt
make install-dev
```

Three commands become available globally: `habitt`, `tico`, `tracker`.

### Shell Completion (optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
eval "$(_HABITT_COMPLETE=source_zsh habitt)"
eval "$(_TICO_COMPLETE=source_zsh tico)"
eval "$(_TRACKER_COMPLETE=source_zsh tracker)"
```

---

## Quick Start

### Launch the main menu

```bash
habitt
```

Arrow keys to navigate, Enter to select, `q` to go back.

### Direct access

```bash
habitt todo          # Open tico directly
habitt track         # Open tracker directly
```

### Todo commands (CLI)

```bash
tico add "Buy groceries" --tag personal
tico list
tico list --tag work
tico done 3           # Mark row 3 as done
tico undo 3
tico remove 3
tico export --format csv
```

### Tracker commands (CLI)

```bash
tracker start "Deep work"    # Start timer
tracker pause
tracker resume
tracker stop                 # Stop and save
tracker log                  # Show today's activities
tracker stats                # Weekly statistics
tracker export --format txt  # Export to Desktop
```

---

## Project Structure

```text
habitt/
├── pyproject.toml               # Project metadata and tool configs
├── Makefile                      # Development commands
├── README.md
├── LICENSE
├── .gitignore
├── assets/                       # Assets like logos
│   └── Tico.png
├── src/                          # Source code
│   └── habitt/
│       ├── __init__.py
│       ├── cli.py                # Launcher (habitt command)
│       ├── __main__.py           # python -m habitt
│       ├── core/                 # Shared utilities
│       ├── tico/                 # Todo manager
│       ├── tracker/              # Activity logger
│       ├── plugins/              # Built-in plugins
│       └── assets/               # Built-in resources
│           └── music/
└── tests/                        # Test suite
    ├── conftest.py
    └── ...
```

---

## Development

```bash
make install-dev   # Install with dev dependencies
make format        # Run black and ruff
make lint          # Run ruff linter
make lint-fix      # Auto-fix lint issues
make type-check    # Run mypy
make test          # Run pytest
make test-cov      # Run tests with coverage (80%+ required)
make clean         # Remove build artifacts
```

Pre-commit hooks automatically format and lint code before every commit.

---

## Plugins

### Built-in Plugins

| Plugin          | Description                                   |
| --------------- | --------------------------------------------- |
| **Calendar**    | Shamsi monthly calendar with Persian weekdays |
| **Pomodoro**    | Configurable work/break cycles                |
| **Quick Notes** | Simple note-taking with search and export     |

### Creating a Custom Plugin

1. Create a folder in `~/.habitt/plugins/your-plugin/`
2. Add an `__init__.py` with a class inheriting from `PluginBase`:

```python
from habitt.core.plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "my-plugin"
    description = "What it does"

    def run_tui(self):
        # Your TUI code here
        pass
```

1. Restart Habitt – your plugin appears in the Plugins menu.

---

## Data Storage

All data lives in `~/.habitt/`:

- `tico.json` – tasks
- `tracker.json` – activities
- `focus_config.json` – focus settings
- `backups/` – automatic backups (last 10 versions)
- `themes/` – custom theme JSON files
- `plugins/` – user-installed plugins
- `focus_music/` – user's focus music files

Data directory can be changed from Settings.

---

## License

MIT – see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [Rich](https://github.com/Textualize/rich) – stunning terminal UI
- [jdatetime](https://github.com/slashmili/python-jalali) – Jalali date support
- [Click](https://click.palletsprojects.com/) – CLI framework
- [readchar](https://github.com/magmax/python-readchar) – key press detection
- [pytest](https://pytest.org/) – testing framework

---

Made with ❤️ for terminal dwellers.
