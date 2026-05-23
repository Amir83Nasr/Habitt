.PHONY: help install dev-install test lint format type-check clean

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	python3 -m pip install .

install-dev: ## Install with development dependencies
	python3 -m pip install -e ".[dev]"

test: ## Run tests with pytest
	pytest

test-cov:
	pytest --cov=habitt --cov-report=term --cov-report=html --cov-fail-under=70 tests/

lint: ## Lint source and test files with ruff
	ruff check habitt/ tests/

lint-fix: ## Lint and fix source and test files with ruff
	ruff check --fix habitt/ tests/

format: ## Format code with black and ruff
	isort habitt/ tests/
	black habitt/ tests/
	ruff format habitt/ tests/

type-check: ## Type-check with mypy
	mypy habitt/

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache .ruff_cache htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish:
	rm -rf dist/
	python -m build
	twine upload dist/*