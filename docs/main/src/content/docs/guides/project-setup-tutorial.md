---
title: Project Setup Tutorial
description: Tutorial paso a paso para instalar, configurar y levantar Yastubo Backend con flujo recomendado.
---

## Objetivo

Este tutorial deja tu entorno listo para desarrollar en local con calidad y tests automatizados.

## 1) Prerrequisitos

- Python 3.12
- `uv`
- MySQL 8+
- Redis 7+
- Git

## 2) Clonar y entrar al proyecto

```bash
git clone https://github.com/TechAtlasDev/yastubo_backend.git
cd yastubo_backend_v1
```

## 3) Setup automático recomendado (un comando)

```bash
uv run python scripts/backend_setup.py
```

Este comando hace:

1. `uv sync --dev`
2. instala hooks de `pre-commit` y `pre-push`
3. `alembic upgrade head`
4. `python scripts/seed_roles.py`
5. smoke test de infraestructura

## 4) Ejecutar API

```bash
uv run uvicorn app.main:app --reload
```

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`

## 5) Flujo diario recomendado

Antes de commitear:

```bash
uv run python scripts/build.py
```

Este es el equivalente al “build” de JS para este backend: asegura lint + tests.

## 6) Si quieres setup manual

```bash
cp .env.example .env
uv sync --dev
uv run alembic upgrade head
uv run python scripts/seed_roles.py
PYTHONPATH=$PWD uv run pytest tests/test_infra.py -q
```

## 7) Troubleshooting rápido

### `ModuleNotFoundError: No module named 'app'`

Usa:

```bash
PYTHONPATH=$PWD uv run pytest -q
```

### Problemas con migraciones

Verifica `.env` y que `DATABASE_URL_SYNC` apunte a una base accesible.

### Redis no responde

Verifica `REDIS_URL` y que Redis esté levantado.
