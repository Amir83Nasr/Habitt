.PHONY: help install dev-install test lint format type-check clean

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install .

dev-install: ## Install with development dependencies
	pip install -e ".[dev]"

install-completion:
	@echo "Add these lines to your ~/.zshrc or ~/.bashrc:"
	@echo 'eval "$$(_HABITT_COMPLETE=source_zsh habitt)"'
	@echo 'eval "$$(_TICO_COMPLETE=source_zsh tico)"'
	@echo 'eval "$$(_TRACKER_COMPLETE=source_zsh tracker)"'

test: ## Run tests with pytest
	pytest

test-cov:
	pytest --cov=src/habitt --cov-report=term --cov-report=html --cov-fail-under=80 tests/

lint: ## Lint source and test files with ruff
	ruff check src/ tests/

lint-fix: ## Lint and fix source and test files with ruff
	ruff check --fix src/ tests/

format: ## Format code with black and ruff
	isort src/ tests/
	black src/ tests/
	ruff format src/ tests/

type-check: ## Type-check with mypy
	mypy src/

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete