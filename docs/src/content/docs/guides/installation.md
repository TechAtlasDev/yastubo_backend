---
title: Installation & Setup
description: Guide to install and configure the project environment.
---

## Requisitos

- Python 3.12
- uv
- MySQL 8+
- Redis 7+

## Setup recomendado

```bash
uv run python scripts/backend_setup.py
```

Este comando prepara todo automáticamente.

## Setup manual

1. Crear archivo de entorno:

```bash
cp .env.example .env
```

2. Instalar dependencias:

```bash
uv sync --dev
```

3. Ejecutar migraciones:

```bash
uv run alembic upgrade head
```

4. Sembrar roles y permisos:

```bash
uv run python scripts/seed_roles.py
```

5. Verificar infraestructura:

```bash
PYTHONPATH=$PWD uv run pytest tests/test_infra.py -q
```

6. Levantar API:

```bash
uv run uvicorn app.main:app --reload
```
