# Contributing to Habitt

Thank you for your interest in contributing to Habitt!

## Development Setup

1. Clone the repository.
2. Install development dependencies:
   ```bash
   make install-dev
   ```
3. Run tests to ensure everything is working:
   ```bash
   make test
   ```

## Commit Pattern

We follow a simple commit message pattern using tags in brackets. Please adhere to this format:

| Tag | Usage |
| :--- | :--- |
| `[ ADD ]` | For new features or files. |
| `[ FIX ]` | For bug fixes. |
| `[ CHANGE ]` | For refactoring or modifications. |
| `[ VERSION ]` | For version bumps. |

Example:
```text
[ ADD ] Add new calendar plugin
[ FIX ] Fix timer pause bug
```

## Pull Request Process

1. Ensure your code passes all tests (`make test`) and type-checks (`make type-check`).
2. Follow the commit pattern above.
3. Submit a pull request.
