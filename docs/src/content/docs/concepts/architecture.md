---
title: Arquitectura
description: Diseño modular y límites de dominio en Yastubo.
---

La arquitectura de Yastubo Backend v1 está diseñada siguiendo principios de **Modular Monolith**, donde la claridad en los límites de dominio permite que el sistema crezca sin que el código se convierta en una "bola de lodo" inmanejable.

## Key Features

*   **Modularidad Estricta:** Cada módulo en `app/modules` tiene sus propias responsabilidades, modelos de datos, esquemas y lógica de negocio.
*   **Comunicación Interna Basada en Servicios:** Los módulos no acceden directamente a las tablas de otros módulos; utilizan inyección de dependencias para invocar servicios.
*   **Shared Core:** Elementos transversales como la conexión a bases de datos, manejo de excepciones y utilidades residen en `app/core` y `app/shared`.

## Deep Dive Técnico: Organización de Módulos

Cada dominio del negocio (ej. `plans`, `emission`, `payments`) está encapsulado. Una estructura típica de un módulo se ve así:

```text
app/modules/emission/
├── models.py      # Definición de tablas en SQLAlchemy
├── schemas.py     # Validaciones de Pydantic
├── service.py     # Lógica central del negocio
├── router.py      # Endpoints de la API
└── state_machine.py # Lógica de ciclo de vida
```

### Límites de Dominio (Domain Boundaries)

1.  **Auth (Identidad):** Gestiona usuarios, roles y autenticación JWT. No sabe nada de pólizas.
2.  **Plans (Lógica Actuarial):** Define productos, coberturas y recargos por edad. Es el motor de cálculo.
3.  **Emission (Negocio Core):** Gestiona pólizas y beneficiarios. Depende de `Plans` para saber qué está emitiendo.
4.  **Payments (Fintech):** Abstracción total de Stripe. Gestiona suscripciones y eventos de pago.
5.  **Audit (Cross-cutting):** Inyecta trazabilidad en todos los demás módulos sin "ensuciar" el código de negocio.

## Ejemplo de Implementación: Router Modular

```python
# app/main.py
from app.modules.emission.router import router as emission_router
from app.modules.payments.router import router as payments_router

# Los routers se montan en el punto de entrada, manteniendo el aislamiento
api_v1_router.include_router(emission_router)
api_v1_router.include_router(payments_router)
```
*Este enfoque permite desactivar o refactorizar módulos enteros sin afectar la estabilidad global de la aplicación.*

## Proceso de una Petición (Request Flow)

![Architecture Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844057/8398378e-c6bf-41af-a3b5-e76f745b52c7.png)
