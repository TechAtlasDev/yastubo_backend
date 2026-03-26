---
title: Project Philosophy
description: Principios de diseño y decisiones de ingeniería del backend.
---

## 1. Seguridad por defecto

- autenticación obligatoria en endpoints sensibles
- autorización por rol
- auditoría de acciones críticas

## 2. Modularidad antes que microservicios

Se prioriza modularidad interna con límites explícitos por dominio.

## 3. Best-effort en integraciones no críticas

CRM y notificaciones no bloquean el flujo principal de negocio.

## 4. Calidad continua

Toda contribución debe pasar quality gate:

```bash
uv run python scripts/build.py
```

## 5. Evolución incremental

Cambios pequeños, testeables y trazables por fase.

## 6. Operabilidad

- logs claros
- jobs programados
- CI/CD reproducible
