---
title: Scripts Tutorial
description: Uso práctico de los scripts de automatización (setup, build, tests y utilidades).
---

## Resumen de scripts

| Script | Propósito |
|---|---|
| `scripts/backend_setup.py` | Bootstrap completo del proyecto |
| `scripts/build.py` | Quality gate: lint + tests |
| `scripts/test_console.py` | Runner interactivo para ejecutar tests por módulo/archivo/caso |
| `scripts/seed_roles.py` | Seed inicial de roles y permisos |

## `backend_setup.py`

```bash
uv run python scripts/backend_setup.py
```

Flags útiles:

```bash
--skip-sync
--skip-hooks
--skip-migrations
--skip-seed
--skip-smoke-test
```

## `build.py` (equivalente a npm build)

```bash
uv run python scripts/build.py
```

Incluye:

1. `ruff check .`
2. `pytest -q`

Opciones:

```bash
uv run python scripts/build.py --lint-only
uv run python scripts/build.py --tests-only
uv run python scripts/build.py --fail-fast
```

## `test_console.py` (selector interactivo)

```bash
uv run python scripts/test_console.py
```

Permite elegir:

- suite completa
- módulo específico
- archivo
- node id (`file.py::test_name`)
- filtro por `-k`

Modo CLI directo:

```bash
uv run python scripts/test_console.py --all
uv run python scripts/test_console.py --module payments
uv run python scripts/test_console.py --target tests/modules/payments/ -k webhook
```

## Atajos con Makefile

```bash
make setup
make build
make lint
make test
make test-interactive
make hooks
```

## Recomendación de equipo

- Antes de push: `uv run python scripts/build.py`
- Antes de merge: CI verde + review
