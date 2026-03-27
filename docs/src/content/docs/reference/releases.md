---
title: Historial de Lanzamientos (Releases)
description: Registro de cambios y mejoras arquitectónicas del backend de Yastubo.
---

## [0.2.0] - 2026-03-26

### Añadido
- **Módulo de Planes**: Se han incorporado campos de "Periodos de Espera" (*Vesting Periods*) al modelo de `Plan` para automatizar la validación de derechos de asistencia.
    - `vesting_accidental_days`: Días de espera para muerte accidental (por defecto 0).
    - `vesting_natural_days`: Días de espera para muerte natural (por defecto 180).
    - `vesting_suicide_days`: Días de espera para suicidio (por defecto 365).
- **Esquemas de API**: Actualización de los esquemas Pydantic `PlanCreate`, `PlanUpdate` y `PlanResponse` para incluir los nuevos campos.
- **Migraciones**: Nueva revisión de Alembic (`ecb513a9360b`) para actualizar la tabla `plans`.

### Mejoras
- **Capacidad de Soporte**: El sistema ahora es totalmente compatible con la lógica multinacional de planes como "de Ahorita y Siempre" y "Yastubo de Pe a Pa", permitiendo una validación programática de la carencia sin intervención humana.

---

## [0.1.0] - 2026-03-19

### Añadido
- Versión inicial del backend modular.
- Módulos de Autenticación, Planes, Emisiones y Pagos (Stripe).
- Integración básica con IA (Gemini).
