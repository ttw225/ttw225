PKG=src

.PHONY: all clean version init dev run reformat isort black lint ruff pylint mypy analysis bandit test ci-bundle build

init: clean
	@echo Install Environment
	uv sync --no-dev

dev: clean
	@echo Install Develop Environment
	uv sync

run:
	@echo Run Project
	uv run python3 $(PKG)/build_readme.py

reformat: isort black

isort:
	@echo [Reformat] Sort Imports
	uv run isort $(PKG)/

black:
	@echo [Reformat] Code Format
	uv run black $(PKG)

lint: ruff pylint mypy

ruff:
	@echo [Linter] Style Check
	uv run ruff check $(PKG)

pylint:
	@echo [Linter] Style Check
	uv run pylint $(PKG)

mypy:
	@echo [Linter] Type Check
	uv run mypy $(PKG)

analysis: bandit

bandit:
	@echo [Analysis] Static Analysis
	uv run bandit -r ${PKG}/

test:
	uv run python3 -m pytest -vv --cov-report=term-missing --cov=${PKG} tests/

ci-bundle: reformat lint analysis

build:
	docker build . -f cat_readme/Dockerfile -t cat_readme

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -type d -name '*.egg-info' -delete
	find . -type f -name '*.egg' -delete

clean-pyc:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	find . -type d -name '__pycache__' -delete

clean-test:
	rm -rf .pytest_cache
	rm -f .coverage

clean-third-party:
	rm -rf .mypy_cache
	rm -rf db_cache.sqlite
	rm -rf pypi_cache.sqlite

clean: clean-build clean-pyc clean-test clean-third-party
