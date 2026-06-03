# Define colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m # No Color
BOLD := \033[1m

.PHONY: help install install-dev test test-cov lint lint-fix format type-check clean docs-serve docs-build bump publish

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BOLD)$(BLUE)=============================================$(NC)"
	@echo "$(BOLD)$(BLUE)           HABITT MAKEFILE HELP              $(NC)"
	@echo "$(BOLD)$(BLUE)=============================================$(NC)\n"
	@echo "$(BOLD)Usage:$(NC) make [target]\n"
	@echo "$(BOLD)$(YELLOW)--- Development ---$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(install|clean|format|lint|type-check)' | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo "\n$(BOLD)$(YELLOW)--- Testing ---$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep '^test' | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo "\n$(BOLD)$(YELLOW)--- Documentation ---$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep '^docs' | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo "\n$(BOLD)$(YELLOW)--- Publishing ---$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(publish|bump)' | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo "\n"

install: ## Install the package
	python3 -m pip install .

install-dev: ## Install with development dependencies
	python3 -m pip install -e ".[dev]"

test: ## Run tests with pytest
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=src/habitt --cov-report=term --cov-report=html --cov-fail-under=70 tests/

lint: ## Lint source and test files with ruff
	ruff check src/ tests/

lint-fix: ## Lint and fix source and test files with ruff
	ruff check --fix src/ tests/

format: ## Format code with black and ruff
	black src/ tests/
	ruff format src/ tests/

type-check: ## Type-check with mypy
	mypy src/

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache .ruff_cache htmlcov/ .coverage site/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs-serve: ## Serve documentation locally
	mkdocs serve

docs-build: ## Build documentation static site
	mkdocs build

bump: ## Bump version and update changelog
	cz bump

publish: ## Build and publish to PyPI
	rm -rf dist/
	python -m build
	twine upload dist/*
