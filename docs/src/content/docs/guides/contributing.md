---
title: Contributing
description: Guía para contribuir al backend de forma consistente.
---

## Flujo recomendado

1. Crear rama desde `develop`
2. Implementar cambio pequeño y enfocado
3. Ejecutar quality gate local
4. Abrir PR

## Comandos obligatorios antes de PR

```bash
uv run python scripts/build.py
```

## Convenciones

- Python 3.12
- tipado claro
- tests para cambios funcionales
- no mezclar refactors grandes con features

## Hooks de git

Instalar una vez:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

> `scripts/backend_setup.py` ya lo hace automáticamente.

## Checklist de Pull Request

- [ ] lint en verde
- [ ] tests en verde
- [ ] docs actualizadas
- [ ] no hay secretos en código
