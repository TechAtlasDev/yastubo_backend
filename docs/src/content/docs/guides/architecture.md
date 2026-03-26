---
title: Architecture
description: Arquitectura del backend y cómo se organizan los módulos.
---

## Estilo arquitectónico

Yastubo usa un **monolito modular** en Python.

Ventajas buscadas:

- menor complejidad operativa
- evolución rápida por fases
- límites claros por dominio

## Estructura principal

- `app/core`: configuración, DB, Redis, logging
- `app/modules/*`: dominios de negocio
- `app/shared`: componentes comunes
- `app/workers`: tareas asíncronas (ARQ)
- `migrations`: Alembic
- `tests`: suite funcional e integración

## Módulos de dominio

- `auth`: JWT, roles, permisos
- `plans`: planes, coberturas, cálculo de precio
- `emission`: clientes, pólizas, estados, PDF
- `payments`: Stripe, suscripciones, webhooks
- `audit`: trazabilidad de acciones
- `portal`: autoservicio cliente
- `notifications`: email/WhatsApp
- `crm`: sync best-effort con Zoho

## Patrón por módulo

En general cada módulo mantiene:

- `models.py`
- `schemas.py`
- `service.py`
- `router.py`

Esto separa:

- persistencia
- contratos de entrada/salida
- reglas de negocio
- capa HTTP

## Integraciones externas

- Stripe (pagos + webhook)
- SendGrid (email)
- Twilio WhatsApp
- Zoho CRM

Todas se diseñan para ser **mockeables** y controladas por feature flags.

## Calidad y entrega

- lint con Ruff
- tests con pytest
- quality gate local en `scripts/build.py`
- CI/CD en GitHub Actions
