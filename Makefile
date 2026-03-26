SHELL := /bin/bash

.PHONY: help setup build lint test test-interactive smoke hooks

help:
	@echo "Comandos disponibles:"
	@echo "  make setup            # instalación + inicialización (Rich)"
	@echo "  make build            # quality gate (lint + tests)"
	@echo "  make lint             # solo lint"
	@echo "  make test             # suite completa"
	@echo "  make test-interactive # selector interactivo de tests"
	@echo "  make smoke            # tests de infraestructura"
	@echo "  make hooks            # instala hooks de pre-commit"

setup:
	uv run python scripts/backend_setup.py

build:
	uv run python scripts/build.py

lint:
	uv run ruff check .

test:
	PYTHONPATH=$$PWD uv run pytest -q

test-interactive:
	uv run python scripts/test_console.py

smoke:
	PYTHONPATH=$$PWD uv run pytest tests/test_infra.py -q

hooks:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push
