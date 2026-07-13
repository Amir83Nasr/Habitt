# Habitt

![Habitt Logo](assets/Tico.png)

**Terminal-based habit tracker.** Todo manager (tico), activity logger (tracker), and extensible plugin system — all from the command line.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/Amir83Nasr/habitt/actions/workflows/ci.yml/badge.svg)](https://github.com/Amir83Nasr/habitt/actions/workflows/ci.yml)

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Development](#development)
- [Testing](#testing)
- [Plugins](#plugins)
- [Data Storage](#data-storage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 📋 Tico – Todo Manager

- Markdown-style checkboxes (`[x]` / `[ ]`).
- Tag-based organization (`#work`, `#personal`, `#study`).
- Arrow-key navigable menu.
- Add, toggle, and remove tasks by row number.
- Filter by tag.
- Bulk operations — toggle or remove multiple tasks at once.

### ⏱️ Tracker – Activity Logger

- Log daily activities with start/end times.
- Live timer with pause, resume, and stop.
- Manual time entry with automatic date and time validation.
- Daily and weekly statistics with bar chart summaries.
- Export to JSON, CSV, or TXT.

### 🧩 Plugin System

- Built-in plugins: Calendar (Shamsi), Pomodoro Timer, Quick Notes.
- User plugins via `~/.habitt/plugins/` — write in Python.
- Automatic discovery of user and built-in plugins.

### 🎨 Custom Themes

- 12 built-in color themes (blue_purple, forest, ocean, sunset, nord, and more).
- Custom themes via JSON files in `~/.habitt/themes/`.
- Live preview in the settings menu.

### 🛡️ Data Safety

- Automatic backups (last 10 versions retained).
- JSON storage in `~/.habitt/` — no database server required.
- Validated date/time input to prevent corruption.

### ⌨️ Terminal Experience

- Arrow-key navigation across all menus.
- Single-key shortcuts for frequent actions.
- Tab completion for CLI commands (bash/zsh).
- Rich-based tables, panels, and progress bars.

---

## Technology Stack

| Layer          | Technology                                                  |
| -------------- | ----------------------------------------------------------- |
| Language       | [Python](https://www.python.org/) 3.9+                      |
| TUI            | [Rich](https://github.com/Textualize/rich)                  |
| CLI            | [Click](https://click.palletsprojects.com/)                 |
| Calendar       | [jdatetime](https://github.com/slashmili/python-jalali)     |
| Key Detection  | [readchar](https://github.com/magmax/python-readchar)       |
| Linting        | [Ruff](https://docs.astral.sh/ruff/)                        |
| Formatting     | [Black](https://github.com/psf/black)                       |
| Type Checking  | [mypy](https://mypy-lang.org/)                              |
| Testing        | [pytest](https://pytest.org/) / [pytest-cov](https://pytest-cov.readthedocs.io/) |
| CI             | [GitHub Actions](.github/workflows/ci.yml)                  |

---

## Architecture

Habitt is structured as a Python package with three user-facing CLI entry points and a shared core library.

```
habitt          →  habitt/cli.py       Main menu launcher
tico            →  habitt/tico/cli.py  Todo manager
tracker         →  habitt/tracker/cli.py  Activity logger
```

The **core** module provides shared utilities — configuration management, backup rotation, theme loading, notification support, and the plugin base class. Each sub-application (tico, tracker) follows a model–manager–CLI–TUI separation within its own package. Plugins are loaded at runtime through a discovery mechanism that scans both built-in paths and user directories.

---

## Project Structure

```text
habitt/
├── pyproject.toml               # Project metadata and tool configuration
├── Makefile                     # Development convenience targets
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .pre-commit-config.yaml      # Pre-commit hook definitions
├── .github/workflows/ci.yml     # CI pipeline
├── assets/                      # Project assets (logo, etc.)
│   └── Tico.png
├── src/
│   └── habitt/
│       ├── __init__.py
│       ├── __main__.py          # python -m habitt entry point
│       ├── cli.py               # Main CLI (habitt command)
│       ├── core/                # Shared utilities
│       │   ├── config.py
│       │   ├── backup.py
│       │   ├── plugin_base.py
│       │   ├── menu_utils.py
│       │   ├── jalali_helper.py
│       │   ├── notify.py
│       │   ├── report.py
│       │   ├── gamification.py
│       │   └── ...              # Additional helpers
│       ├── tico/                # Todo manager (tico)
│       │   ├── cli.py
│       │   ├── tui.py
│       │   ├── models.py
│       │   └── todo_manager.py
│       ├── tracker/             # Activity logger (tracker)
│       │   ├── cli.py
│       │   ├── tui.py
│       │   ├── models.py
│       │   └── tracker_manager.py
│       ├── plugins/             # Built-in plugins
│       │   ├── calendar/
│       │   ├── pomodoro/
│       │   └── notes/
│       └── assets/music/        # Built-in focus music
└── tests/                       # Test suite (mirrors src structure)
    ├── conftest.py
    ├── core/
    ├── tico/
    ├── tracker/
    ├── plugins/
    └── habitt/
```

---

## Prerequisites

- Python 3.9 or later.
- pip.
- A terminal that supports Unicode and 256-color output (modern terminals on macOS, Linux, and Windows Terminal).

## Installation

### From PyPI (recommended)

```bash
pip install habitt
```

### From source (development mode)

```bash
git clone https://github.com/your-username/habitt.git
cd habitt
make install-dev
```

After installation, three commands become available globally: `habitt`, `tico`, and `tracker`.

### Shell Completion (optional)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
eval "$(_HABITT_COMPLETE=source_zsh habitt)"
eval "$(_TICO_COMPLETE=source_zsh tico)"
eval "$(_TRACKER_COMPLETE=source_zsh tracker)"
```

Substitute `source_zsh` with `source_bash` for bash.

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
tracker start "Deep work"    # Start live timer
tracker pause
tracker resume
tracker stop                 # Stop and save
tracker log                  # Show today's activities
tracker stats                # Weekly statistics
tracker export --format txt  # Export to Desktop
```

---

## Development

Install development dependencies and use the Makefile for common tasks:

```bash
make install-dev        # Install with dev dependencies
```

| Command            | Description                         |
| ------------------ | ----------------------------------- |
| `make format`      | Format code with Black and Ruff     |
| `make lint`        | Run Ruff linter                     |
| `make lint-fix`    | Auto-fix lint issues                |
| `make type-check`  | Run mypy static type checking       |
| `make test`        | Run pytest                          |
| `make test-cov`    | Run tests with coverage (≥70%)      |
| `make clean`       | Remove build artifacts and caches   |
| `make docs-serve`  | Serve documentation locally         |
| `make docs-build`  | Build documentation site            |
| `make bump`        | Bump version and update changelog   |
| `make publish`     | Build and publish to PyPI           |

Pre-commit hooks (Ruff, mypy, end-of-file fixer) run automatically on every commit after installation:

```bash
pre-commit install
```

### CI Pipeline

The [CI workflow](.github/workflows/ci.yml) runs linting, type checking, and tests on every push and pull request to the `main` branch.

---

## Testing

Tests are located in `tests/`, mirroring the source package structure.

```bash
make test          # Run all tests
make test-cov      # Run with coverage report (HTML and terminal)
```

The project uses pytest with coverage tracking. A minimum coverage threshold of 70% is enforced.

---

## Plugins

### Built-in Plugins

| Plugin          | Description                                   |
| --------------- | --------------------------------------------- |
| **Calendar**    | Shamsi (Jalali) monthly calendar with Persian weekday names |
| **Pomodoro**    | Configurable work/break cycle timer           |
| **Quick Notes** | Simple note-taking with search and export     |

### Creating a Custom Plugin

1. Create a folder in `~/.habitt/plugins/your-plugin/`.
2. Add `__init__.py` with a class inheriting from `PluginBase`:

```python
from habitt.core.plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "my-plugin"
    description = "What it does"

    def run_tui(self):
        # Your TUI code here
        pass
```

1. Restart Habitt. The plugin appears in the Plugins menu automatically.

---

## Data Storage

All user data lives in `~/.habitt/`:

| Path                       | Contents                              |
| -------------------------- | ------------------------------------- |
| `tico.json`                | Todo tasks                            |
| `tracker.json`             | Activity logs                         |
| `focus_config.json`        | Focus session settings                |
| `backups/`                 | Automatic backups (last 10 versions)  |
| `themes/`                  | Custom theme JSON files               |
| `plugins/`                 | User-installed plugins                |
| `focus_music/`             | User's focus music files              |

The data directory can be changed from the Settings menu.

---

## Roadmap

- [ ] Desktop notifications for session events.
- [ ] Focus mode with Lo-Fi music integration.
- [ ] Gamification — streaks, XP, and achievements.
- [ ] Data sync across machines.
- [ ] Additional export formats (PDF, Markdown).
- [ ] iCal/CalDAV integration for calendar plugin.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide, covering:

- Development setup and prerequisites.
- Coding standards (Black, Ruff, mypy).
- Branch naming and commit conventions.
- Pull request workflow and code review expectations.

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Amir Hossein Nasrollahi.

---

## Acknowledgements

- [Rich](https://github.com/Textualize/rich) — beautiful terminal formatting.
- [jdatetime](https://github.com/slashmili/python-jalali) — Jalali date support.
- [Click](https://click.palletsprojects.com/) — CLI framework.
- [readchar](https://github.com/magmax/python-readchar) — key press detection.
- [pytest](https://pytest.org/) — testing framework.
