---
title: Audit-First Design
description: Por qué cada cambio importa (Motor de Auditoría).
---

En Yastubo, la transparencia es una característica del producto, no una ocurrencia tardía. Nuestro enfoque **Audit-First** asegura que cada acción significativa —desde la emisión de una póliza hasta un ajuste de precio en Stripe— sea registrada, trazable y responsable.

## Core Benefits

*   **Trazabilidad Total:** Registro automático de quién hizo qué, cuándo y sobre qué entidad.
*   **Cumplimiento Normativo:** Cumple con las exigencias de transparencia de las aseguradoras y entidades financieras.
*   **Depuración Simplificada:** Permite rastrear errores de lógica o de usuario al tener un historial completo de cambios.

## Deep Dive Técnico: El Decorador @audited

El corazón de nuestro sistema de auditoría es un decorador de Python que se aplica a los métodos de servicio. Esto permite separar la lógica de auditoría de la lógica de negocio, manteniendo el código limpio (Clean Code).

### Funcionamiento del Decorador

El decorador `@audited` utiliza introspección de funciones para capturar argumentos, el usuario actual y el resultado de la operación.

```python
# app/modules/audit/decorator.py

def audited(action: str, entity: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Captura de db, usuario y argumentos de la función...
            
            # Ejecución del servicio de negocio
            result = await func(*args, **kwargs)

            # Si la ejecución fue exitosa, registramos la acción
            await audit_service.log(
                db=db,
                action=action,
                entity=entity,
                user_id=user_id,
                entity_id=getattr(result, "id", None),
            )
            return result
        return wrapper
    return decorator
```

### Automatización y Bajo Acoplamiento

Al usar este enfoque, añadir auditoría a una nueva funcionalidad es tan sencillo como añadir una línea de código:

```python
@audited(action="create_lead", entity="lead")
async def create_lead(db: AsyncSession, lead_data: LeadCreate, current_user: User):
    # Lógica de creación del lead...
```
*El sistema se encarga automáticamente de persistir este evento en la tabla `audit_logs` con toda la información de contexto necesaria.*

## Los Audit Logs

Cada entrada en el log de auditoría captura una instantánea del evento:

*   **Action:** El nombre semántico de la acción (ej. `activate_policy`).
*   **Entity:** El tipo de objeto afectado (ej. `policy`).
*   **Entity ID:** El identificador único del recurso.
*   **User ID:** Quién realizó la acción (o `None` si fue un proceso automático del sistema).
*   **Timestamp:** Fecha y hora exacta del evento.

## Flujo de Auditoría Automática

![Audit-First Design Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844287/7e37a080-f34f-44e0-9a24-794ce5856901.png)
