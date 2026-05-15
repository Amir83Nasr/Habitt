# Contributing to Habitt

First of all, **thank you** for considering contributing to Habitt!  
We're excited to have you on board.

This document will guide you through the process of setting up your
development environment, making changes, and submitting them for review.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Ideas for Contribution](#ideas-for-contribution)

## Code of Conduct

Be respectful, constructive, and open-minded.  
We're building this for fun and learning – let's keep it that way.

## Getting Started

1. **Fork** the repository to your GitHub account.
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/your-username/habitt.git
   cd habitt
   ```

3. Add the upstream remote:

   ```bash
   git remote add upstream https://github.com/original/habitt.git
   ```

## Development Setup

Habitt uses a clean Python project structure with `pyproject.toml`.  
You need **Python 3.9 or higher**.

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. Install in development mode with all dev tools:

   ```bash
   make dev-install
   ```

   This runs `pip install -e ".[dev]"` which also installs:
   - `black` – code formatter
   - `ruff` – linter and formatter
   - `mypy` – static type checker
   - `pytest` – test runner
   - `pre-commit` – git hooks

3. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

Now the commands `habitt`, `tico`, and `tracker` are available in your PATH
and will automatically reflect any code changes you make.

## Project Structure

```bash
habitt/
├── pyproject.toml               # Project metadata and tool configs
├── Makefile                      # Convenient dev commands
├── CONTRIBUTING.md
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── src/
│   └── habitt/                   # Main package
│       ├── __init__.py
│       ├── __version__.py
│       ├── cli.py                # Launcher (habitt command)
│       ├── __main__.py           # python -m habitt
│       ├── core/                 # Shared utilities
│       │   ├── config.py         # Paths and configuration
│       │   ├── storage.py        # JSON file I/O
│       │   ├── themes.py         # Color presets
│       │   ├── jalali_helper.py  # Shamsi date/time functions
│       │   └── validators.py     # Input validation helpers
│       ├── tico/                 # Todo manager
│       │   ├── models.py
│       │   ├── todo_manager.py   # Business logic
│       │   ├── tui.py            # Rich-based terminal UI
│       │   └── cli.py            # Click CLI
│       └── tracker/              # Activity logger
│           ├── models.py
│           ├── tracker_manager.py
│           ├── tui.py
│           └── cli.py
└── tests/                        # Test suite
    ├── conftest.py
    ├── core/
    ├── tico/
    └── tracker/
```

## Making Changes

1. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. Make your changes and test them thoroughly.

3. Run the full linting and test suite:

   ```bash
   make format
   make lint
   make type-check
   make test
   ```

4. Commit your changes (see [Commit Messages](#commit-messages)).

5. Push your branch and open a Pull Request against the `main` branch.

## Code Style

We enforce a consistent code style automatically:

- **Black** for formatting (line length 88, double quotes).
- **Ruff** for linting (replaces flake8, isort, etc.).
- **Mypy** for static type checking (strict mode).

All rules are configured in `pyproject.toml`. Pre-commit hooks will
format and lint your code before every commit automatically.

A few manual guidelines:

- Write code in **English only** – comments, docstrings, UI strings.
- Keep functions small and focused.
- Use type hints everywhere.
- Add docstrings for public functions and classes.
- Do not use emojis in source code.

## Testing

We use `pytest` for testing. Tests are located in the `tests/` directory
and mirror the package structure.

- Run all tests:

  ```bash
  make test
  ```

- Run a specific test file:

  ```bash
  pytest tests/tico/test_todo_manager.py -v
  ```

Tests use a temporary data directory (see `conftest.py`) so they never
touch your real `~/.habitt/` data.

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
feat: add export to JSON for tracker
fix: resolve crash when timer is paused
refactor: move validators to core module
docs: update README with new settings options
```

Keep messages concise and in English.

## Submitting Changes

1. Push your branch to your fork.
2. Open a Pull Request to the original repository.
3. In the PR description, explain **what** you changed and **why**.
4. Make sure all CI checks pass (if set up).
5. Wait for a review. We'll get back to you as soon as possible.

## Reporting Bugs

Found a bug? Open an issue on GitHub with:

- A clear title and description.
- Steps to reproduce the problem.
- Expected vs actual behavior.
- Your OS, Python version, and any relevant error messages.

## Feature Requests

We love new ideas! Open an issue and tag it as `enhancement`.  
Explain the feature, why it's useful, and how you imagine it working.
If you're planning to implement it yourself, mention that too.

## Ideas for Contribution

Here are some areas where you can jump in:

- **Pomodoro timer** – integrate a focus/break cycle into tracker.
- **Keyboard shortcuts** – make the TUI navigable with single keys without prompts.
- **Persian language support** – add translations for the UI.
- **Notifications** – terminal bell or desktop notification when timer ends.
- **Data backup/restore** – automatic backup of JSON files.
- **Improved bar charts** – use Rich's `Bar` for more visual stats.
- **Deadlines for tasks** – due dates with warnings.
- **Custom user themes** – allow defining theme colors in config file.
- **Tab completion** – for Click CLI commands.

Feel free to pick one and start coding!

---

Thank you again for being part of Habitt.  
Let's build something great together. 🚀
