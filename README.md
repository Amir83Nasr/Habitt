# Habitt

**T**erminal **I**ntegrated **C**o**mm**and-line **O**rganizer & **T**racker

Manage your daily tasks and activities from the comfort of your terminal.
Built with [Rich](https://github.com/Textualize/rich), [Click](https://click.palletsprojects.com/),
and love for the command line.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

---

## Features

- **Todo Manager (`tico`)** – simple task lists with checkboxes (`[x]` / `[ ]`) and tags.
- **Activity Tracker (`tracker`)** – log daily activities with a live timer (pause, resume, stop) and weekly statistics.
- **Launcher (`habit`)** – a unified entry point to both tools.
- **Jalali (Shamsi) calendar** – all dates and times in Asia/Tehran timezone.
- **Rich TUI** – beautiful terminal interface with panels, tables, and layouts.
- **CLI mode** – fast command-line access for scripting and power users.
- **JSON storage** – no database servers, data lives in `~/.habitt/`.
- **Dev tools** – pre-configured `black`, `ruff`, `mypy`, `pre-commit`, and `pytest`.

---

## Installation

Clone and install in development mode:

```bash
git clone https://github.com/yourusername/habitt.git
cd habitt
pip install -e ".[dev]"
pre-commit install
```

The three commands `habit`, `tico`, `tracker` will now be available system-wide.

---

## Usage

### Launcher

```bash
habit
# Shows a menu to enter tico or tracker

habit todo      # Open tico directly
habit track     # Open tracker directly
```

### Tico – Todo Manager

**Interactive TUI**  
Run `tico` (or `habit todo`) to enter the menu, then:

- View all tasks
- Add a task with optional tag
- Toggle done/undone
- Remove a task
- Filter by tag

**CLI shortcuts**

```bash
tico add "buy groceries" --tag personal
tico list
tico list --tag work
tico done <task_id>
tico undo <task_id>
tico remove <task_id>
```

Task display uses checkboxes:

```bash
[x] Done task        #tag
[ ] Open task        #another_tag
```

### Tracker – Activity Logger

**Interactive TUI**  
Run `tracker` (or `habit track`) to:

- Show today's logged activities
- Add an activity manually (with Shamsi times)
- Start a live timer with **p**ause, **r**esume, **s**top & save, **q**uit
- View daily statistics for the last 7 days (including a simple bar chart)

**CLI shortcuts**

```bash
tracker start "deep work"   # Start a new timer
tracker pause               # Pause the timer
tracker resume              # Resume the timer
tracker stop                # Stop timer and save activity
tracker log                 # Show today's activities
tracker stats               # Show 7‑day summary
```

---

## Data Storage

All data is saved as JSON files in `~/.habitt/`:

- `tico.json` – todo items
- `tracker.json` – logged activities
- `timer_state.json` – temporary timer state (for CLI mode)

---

## Project Structure

```
habitt/
├── pyproject.toml
├── Makefile
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
└── habitt/
    └── habitt/
        ├── __init__.py
        ├── core/
        │   ├── config.py
        │   ├── storage.py
        │   ├── themes.py
        │   └── jalali_helper.py
        ├── tico/
        │   ├── models.py
        │   ├── todo_manager.py
        │   ├── tui.py
        │   └── cli.py
        ├── tracker/
        │   ├── models.py
        │   ├── tracker_manager.py
        │   ├── tui.py
        │   └── cli.py
        └── habit/
            ├── tui.py
            └── cli.py
```

---

## Development

```bash
make dev-install   # Install with dev dependencies
make format        # Run black and ruff
make lint          # Run ruff linter
make type-check    # Run mypy
make test          # Run pytest (once tests are added)
make clean         # Remove build artifacts
```

Pre-commit hooks will automatically format and lint your code before every commit.

---

## License

MIT. See `pyproject.toml` for details.

---

## Acknowledgements

- [Rich](https://github.com/Textualize/rich) for the stunning terminal UI
- [jdatetime](https://github.com/slashmili/python-jalali) for Jalali date support
- [Click](https://click.palletsprojects.com/) for the CLI framework

---

Made with ❤️ for terminal dwellers.
