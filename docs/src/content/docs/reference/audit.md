---
title: Audit (Trazabilidad Total)
description: Registro automático de acciones, trazabilidad de entidades y auditoría de seguridad.
---

El módulo de **Audit** es el pilar de transparencia de Yastubo. Implementa una capa de observabilidad que registra cada cambio crítico en el sistema, vinculándolo a un usuario, una entidad y una marca de tiempo inalterable.

## Key Features

*   **Decorator-Based Auditing**: Los desarrolladores pueden auditar cualquier función de servicio simplemente añadiendo el decorador `@audited`.
*   **Trazabilidad de Entidades**: Permite reconstruir el historial de cambios de una póliza, un usuario o un plan desde su creación.
*   **Identificación de Actores**: Registra automáticamente quién realizó la acción, incluso en flujos complejos con múltiples intervinientes.
*   **Persistencia de Logs**: Los registros se almacenan en una tabla dedicada (`audit_logs`) diseñada para consultas rápidas y cumplimiento normativo.

:::tip[Buenas Prácticas]
Utiliza siempre `@audited` en funciones que muten el estado de la base de datos. Esto facilita la resolución de conflictos y el soporte técnico al permitir ver exactamente cuándo y quién cambió un dato.
:::

## Deep Dive Técnico

### El Decorador `@audited`
El núcleo de la auditoría reside en un decorador inteligente que:
1.  **Analiza la firma**: Inspecciona los argumentos de la función para extraer la sesión de base de datos (`db`) y el ID del usuario (`user_id`).
2.  **Ejecuta y Captura**: Llama a la función original y captura el resultado.
3.  **Extracción de ID de Entidad**: Si la función devuelve un objeto (ej. una Póliza), el decorador extrae automáticamente su ID para vincularlo al log.
4.  **Auditoría Asíncrona**: Registra la acción en la base de datos de forma asíncrona sin bloquear la respuesta al cliente.

### Estructura de un Log de Auditoría
Cada entrada en el log contiene:
*   **`action`**: El nombre semántico de la acción (ej. `POLICY_ISSUED`).
*   **`entity`**: El nombre de la tabla o entidad afectada (ej. `Policy`).
*   **`entity_id`**: El UUID del registro específico que fue modificado.
*   **`user_id`**: El UUID del usuario que ejecutó la operación.
*   **`timestamp`**: Fecha y hora exacta de la acción.

## Ejemplo Práctico: Implementación del Decorador

El siguiente código muestra cómo se aplica la auditoría de forma transparente en un servicio:

```python
@audited(action="PLAN_CREATED", entity="Plan")
async def create_plan(
    db: AsyncSession, 
    data: PlanCreate, 
    created_by: uuid.UUID
) -> Plan:
    """
    Crea un nuevo plan. 
    Gracias al decorador, el sistema registrará automáticamente:
    - Que se creó un 'Plan'
    - El ID del plan generado (extraído del retorno)
    - Quién lo creó (extraído del argumento 'created_by')
    """
    plan = Plan(**data.model_dump())
    db.add(plan)
    await db.commit()
    return plan
```

## Diagrama de Proceso

![Audit Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774845030/80f0f4d3-31bb-4d95-9c52-ecf5f158ef74.png)

## Estructura del Log (Modelo)

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | UUID | Identificador único del log. |
| `action` | String | Acción realizada (ej. `USER_LOGIN`). |
| `entity` | String | Tipo de entidad afectada. |
| `entity_id` | UUID | ID del recurso específico. |
| `user_id` | UUID | ID del autor de la acción. |
| `created_at` | DateTime | Marca de tiempo del registro. |
