# Contributing to Habitt

Thanks for your interest in contributing to Habitt. This document covers the workflow, conventions, and expectations for contributors.

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Running the Project](#running-the-project)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Linting and Formatting](#linting-and-formatting)
- [Branch Naming](#branch-naming)
- [Commit Message Conventions](#commit-message-conventions)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Issue Reporting](#issue-reporting)
- [Code Review](#code-review)
- [Communication](#communication)

## Project Overview

Habitt is a terminal-based habit tracker with three integrated tools:

- **Tico** — todo manager with markdown-style checkboxes and tag-based organization.
- **Tracker** — activity logger with a live timer, manual entry, statistics, and export.
- **Plugins** — extensible system for calendar (Shamsi), Pomodoro timer, and quick notes.

Built with Python 3.9+, [Rich](https://github.com/Textualize/rich) for TUI, [Click](https://click.palletsprojects.com/) for CLI, and [jdatetime](https://github.com/slashmili/python-jalali) for Jalali date support.

## Prerequisites

- **Python 3.9 or later**
- **pip** (Python package installer)
- **git**
- **make** (optional, for convenience targets)
- **pre-commit** (optional but recommended; hooks run automatically after `make install-dev`)

## Development Setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/your-username/habitt.git
   cd habitt
   ```

2. Install development dependencies:

   ```bash
   make install-dev
   ```

   Or without `make`:

   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks (recommended):

   ```bash
   pre-commit install
   ```

4. Run the test suite to verify your environment:

   ```bash
   make test
   ```

## Running the Project

After installing in development mode, three commands are available:

```bash
habitt          # Main menu
tico            # Todo manager CLI
tracker         # Activity logger CLI
```

Run directly from source:

```bash
python -m habitt
```

## Coding Standards

Habitt uses a uniform set of tools to keep the codebase consistent.

- **Line length**: 88 characters.
- **Formatting**: [Black](https://github.com/psf/black) (enforced via pre-commit).
- **Import ordering**: [Ruff](https://docs.astral.sh/ruff/) `I` rule (enforced via pre-commit).
- **Type annotations**: All public functions and methods must have type hints checked by [mypy](https://mypy-lang.org/) in strict mode.
- **Naming**: Follow PEP 8 — `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- **Docstrings**: Use Google-style docstrings for public modules, classes, and functions.

Run the formatter and linter before committing:

```bash
make format
make lint
make type-check
```

## Testing

- Write tests for all new features and bug fixes.
- The project uses [pytest](https://pytest.org/) with coverage tracking.
- Run the full suite:

  ```bash
  make test
  ```

- Run with coverage (minimum 70%):

  ```bash
  make test-cov
  ```

- Test files mirror the source structure under `tests/`. Place new tests in the corresponding subdirectory.
- Use `conftest.py` for shared fixtures and configuration.

## Linting and Formatting

The project enforces code quality with pre-commit hooks:

| Hook          | Purpose                                  |
| ------------- | ---------------------------------------- |
| Ruff          | Linting and import sorting (auto-fix)    |
| Ruff-format   | Code formatting (Black-compatible)       |
| mypy          | Static type checking                     |
| end-of-file   | Ensures files end with a newline         |
| trailing-whitespace | Removes trailing whitespace        |

To run all checks manually:

```bash
make lint
make format
make type-check
```

## Branch Naming

Use descriptive, hyphen-separated branch names prefixed by category:

| Prefix        | Purpose          |
| ------------- | ---------------- |
| `feat/`       | New features     |
| `fix/`        | Bug fixes        |
| `refactor/`   | Code changes     |
| `docs/`       | Documentation    |
| `chore/`      | Tooling, CI      |
| `test/`       | Test additions   |

Examples: `feat/dark-theme`, `fix/timer-off-by-one`, `docs/api-readme`.

## Commit Message Conventions

Habitt uses a tagged commit format. Each message consists of a bracketed tag followed by a brief description:

| Tag           | Usage                         |
| :------------ | :---------------------------- |
| `[ ADD ]`     | New features or files         |
| `[ FIX ]`     | Bug fixes                     |
| `[ CHANGE ]`  | Refactoring or modifications  |
| `[ VERSION ]` | Version bumps                 |

Examples:

```text
[ ADD ] Add calendar navigation with month arrows
[ FIX ] Handle empty todo list in export command
[ CHANGE ] Migrate theme loading to lazy initialization
```

Keep the first line under 72 characters. For complex changes, add a blank line followed by a longer body explaining the motivation.

## Pull Request Guidelines

1. Create a branch following the naming convention above.
2. Ensure all tests pass (`make test`) and type checks pass (`make type-check`).
3. Run linting and formatting (`make lint` and `make format`).
4. Keep pull requests focused on a single concern — split unrelated changes into separate PRs.
5. Write a clear PR title and description explaining what changed and why.
6. Link any related issues (e.g., "Closes #42").
7. Expect a review before merge. Address feedback with additional commits.

## Issue Reporting

- Use the [GitHub issue tracker](https://github.com/Amir83Nasr/habitt/issues).
- Search existing issues before opening a new one.
- For bug reports, include:
  - Python version and OS.
  - Steps to reproduce.
  - Expected vs actual behavior.
  - Terminal type (if relevant to display issues).
- For feature requests, describe the use case and any prior art.

## Code Review

- All pull requests require at least one review before merging.
- Reviewers focus on correctness, test coverage, type safety, and adherence to project conventions.
- If a review requests changes, the author should respond with a fix or an explanation.
- Keep discussions constructive and specific.

## Communication

- Use GitHub issues for feature requests, bug reports, and design discussions.
- Use pull request comments for code-level feedback.
- Be respectful and inclusive — follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.
