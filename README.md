# Yastubo Backend

Backend monolítico modular para gestión de planes funerarios.

## Stack

- Python 3.12 + uv
- FastAPI + SQLAlchemy async
- MySQL + Redis
- Alembic
- pytest + ruff
- Textual (TUI)

## Yastubo Dev Machine (CLI) 🚀

Para centralizar el desarrollo, usamos una interfaz interactiva en la terminal que permite gestionar módulos, ejecutar tests y lanzar la documentación.

```bash
make cli
```

**Funcionalidades:**
- **Dashboard:** Estado del sistema y checks de entorno.
- **Modules (Scaffolder):** Crea nuevos módulos con la arquitectura oficial.
- **Testing:** Runner visual para pytest por módulos.
- **Docs:** Lanzar el servidor de Starlight (Astro).
- **Ops:** Atajos de infraestructura.

## Instalación y configuración rápida

### Opción recomendada (1 comando)

```bash
uv run python scripts/backend_setup.py
```

Este setup:
- instala dependencias (`uv sync --dev`)
- instala hooks de git (`pre-commit`, `pre-push`)
- aplica migraciones (`alembic upgrade head`)
- ejecuta seed de roles/permisos
- corre smoke test (`tests/test_infra.py`)

Opciones:

```bash
uv run python scripts/backend_setup.py --skip-migrations
uv run python scripts/backend_setup.py --skip-seed
uv run python scripts/backend_setup.py --skip-smoke-test
uv run python scripts/backend_setup.py --skip-hooks
```

### Opción manual (paso a paso)

```bash
cp .env.example .env
uv sync --dev
uv run alembic upgrade head
uv run python scripts/seed_roles.py
PYTHONPATH=$PWD uv run pytest tests/test_infra.py -q
```

## Scripts principales

### Quality gate (equivalente a "npm run build")

```bash
uv run python scripts/build.py
```

Qué hace:
- lint obligatorio con Ruff
- test suite completa con pytest
- falla inmediatamente si algún paso no pasa

Opciones:

```bash
uv run python scripts/build.py --lint-only
uv run python scripts/build.py --tests-only
uv run python scripts/build.py --fail-fast
```

### Consola interactiva de tests

```bash
uv run python scripts/test_console.py
```

Permite ejecutar:
- suite completa
- módulo completo
- archivo específico
- test puntual por node id
- subconjunto por `-k`

Modo no interactivo:

```bash
uv run python scripts/test_console.py --all
uv run python scripts/test_console.py --module payments
uv run python scripts/test_console.py --target tests/modules/payments/ -k webhook
```

### Atajos con Makefile

```bash
make help
make setup
make build
make lint
make test
make test-interactive
make hooks
make cli              # Yastubo Dev Machine
```

## Cómo aseguramos lint siempre

1. Hooks locales:
	- `pre-commit` y `pre-push` instalados por `backend_setup.py`
	- Configuración en `.pre-commit-config.yaml`
2. CI obligatorio:
	- Workflow de CI ejecuta `scripts/build.py` en push/PR
3. Recomendado en GitHub:
	- branch protection para `main` con status checks requeridos

## CI/CD (GitHub Actions)

- CI: `.github/workflows/ci.yml`
  - push/PR sobre `main` y `develop`
  - ejecuta quality gate (`scripts/build.py`)

- CD: `.github/workflows/cd.yml`
  - al terminar CI con éxito en `main` (o manual)
  - build/push de imagen Docker a GHCR
  - deploy opcional vía SSH

Secrets opcionales para deploy:

- `DEPLOY_SSH_HOST`
- `DEPLOY_SSH_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PATH`

## Documentación adicional

- Guía de instalación: `docs/INSTALLATION.md`
- Guía de scripts: `docs/SCRIPTS.md`
- Filosofía de proyecto: `docs/PROJECT_PHILOSOPHY.md`
- Contribución: `CONTRIBUTING.md`
