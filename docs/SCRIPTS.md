# Scripts disponibles

## scripts/backend_setup.py

Instala e inicializa el backend completo.

```bash
uv run python scripts/backend_setup.py
```

Flags:
- `--skip-sync`
- `--skip-hooks`
- `--skip-migrations`
- `--skip-seed`
- `--skip-smoke-test`

---

## scripts/build.py

Quality gate del proyecto (equivalente a npm build para calidad):

```bash
uv run python scripts/build.py
```

Ejecuta:
1. `ruff check .`
2. `pytest -q`

Flags:
- `--lint-only`
- `--tests-only`
- `--fail-fast`

---

## scripts/test_console.py

Runner interactivo de tests con Rich.

```bash
uv run python scripts/test_console.py
```

Permite seleccionar pruebas por módulo, archivo, test puntual o filtro `-k`.

---

## scripts/seed_roles.py

Crea/actualiza roles y permisos iniciales.

```bash
uv run python scripts/seed_roles.py
```
