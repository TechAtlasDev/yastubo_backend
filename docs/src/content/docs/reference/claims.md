---
title: Claims (Gestión de Siniestros)
description: Reporte de eventos, validación de beneficiarios y gestión de gastos funerarios.
---

El módulo de **Claims** (Siniestros) coordina las acciones necesarias cuando ocurre un evento cubierto por la póliza. Permite la trazabilidad desde el reporte inicial hasta el pago de beneficios o gastos a proveedores de servicios funerarios.

## Key Features

*   **Reporte Multicanal**: Inicio de siniestros vía API, sincronizado con un flujo de trabajo asíncrono.
*   **Gestión de Gastos (Expenses)**: Control detallado de costos asociados a la repatriación o servicios locales.
*   **Event-Driven Integration**: Uso de Pub/Sub (Redis) y tareas en segundo plano (Arq) para procesar siniestros aprobados.
*   **Validación de Beneficiarios**: Sistema de verificación cruzada para asegurar que el pago se realice a la persona correcta.

:::note[Coordinación Asíncrona]
Al aprobar un siniestro, el sistema encola automáticamente tareas para actualizar el estado de la póliza y marcar al asegurado como fallecido, lo que previene futuros cobros de suscripciones.
:::

## Deep Dive Técnico

### Flujo de Resolución de Siniestros
Un siniestro sigue un ciclo de vida gestionado por una máquina de estados simplificada:
1.  **`REPORTED`**: Estado inicial al abrir el caso. Se emite un evento al canal `claims_events` en Redis.
2.  **`UNDER_REVIEW`**: El equipo operativo valida la documentación y vigencia de la póliza.
3.  **`APPROVED`**: Se aprueba el siniestro. Se dispara un job en `Arq` para el procesamiento masivo de cambios.
4.  **`REJECTED` / `RESOLVED`**: Estados finales del siniestro.

### Control de Gastos
El sistema permite añadir múltiples ítems de gasto a un siniestro. Esto es fundamental para la transparencia con los proveedores y el control de los límites de cobertura del plan asociado.

## Ejemplo Práctico: Aprobación de un Siniestro

El siguiente código muestra cómo la aprobación de un siniestro desencadena procesos complejos en segundo plano:

```python
@audited(action="UPDATE_CLAIM_STATUS", entity="Claim")
async def update_claim_status(
    db: AsyncSession,
    claim_id: uuid.UUID,
    status_update: ClaimUpdateStatus,
    user_id: uuid.UUID,
) -> Claim:
    """
    Actualiza el estado de un siniestro.
    Si se aprueba, dispara la lógica de procesamiento asíncrono.
    """
    # 1. Validar la transición de estado legal
    claim = await get_claim(db, claim_id)
    if not can_transition(claim.status, status_update.status):
        raise HTTPException(status_code=400, detail="Transición inválida")

    claim.status = status_update.status
    
    # 2. Si el siniestro se aprueba, encolar procesamiento pesado
    if claim.status == ClaimStatus.APPROVED:
        # Encolamos la tarea en Arq para manejar:
        # - Desactivar suscripciones recurrentes de la póliza
        # - Notificar a aseguradoras aliadas
        # - Actualizar banderas de fallecimiento
        await arq_redis.enqueue_job(
            "process_approved_claim", 
            str(claim.id), 
            str(claim.beneficiary_id)
        )

    await db.commit()
    return claim
```

## Diagrama de Proceso

![Claims Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844975/891f891a-2c66-4db3-a138-cf34fd948c00.png)

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/claims` | Reporte inicial de un siniestro. |
| `PATCH` | `/api/v1/claims/{id}/status` | Cambio de estado y resolución del siniestro. |
| `POST` | `/api/v1/claims/{id}/expenses` | Añadir un desglose de gasto al siniestro. |
| `GET` | `/api/v1/claims/{id}` | Detalle del siniestro y sus gastos asociados. |
