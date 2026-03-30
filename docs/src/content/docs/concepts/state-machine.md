---
title: La Máquina de Estados
description: Entendiendo el ciclo de vida de pólizas y siniestros.
---

En un sistema de seguros, la consistencia de los estados es la base de la confianza. Yastubo implementa un patrón de **Máquina de Estados Finita (FSM)** para asegurar que una póliza o un siniestro nunca entren en una situación de negocio inválida (ej. marcar una póliza como activa sin haber sido pagada).

## Core Benefits

*   **Integridad de Datos:** Solo se permiten transiciones lógicas predefinidas.
*   **Claridad Operativa:** El equipo de soporte puede saber exactamente en qué punto del flujo se encuentra cada cliente.
*   **Automatización Segura:** Los webhooks de Stripe y otros servicios externos solo pueden disparar cambios de estado permitidos.

## Deep Dive Técnico: Transiciones de Póliza

El módulo de emisión define el ciclo de vida de una póliza mediante el objeto `VALID_TRANSITIONS`. Este mapa dicta qué estado puede seguir a otro.

| Origen | Destinos Válidos | Razón de Negocio |
| :--- | :--- | :--- |
| `DRAFT` | `PENDING_PAYMENT`, `CANCELLED` | El lead ha sido creado pero no ha iniciado el pago. |
| `PENDING_PAYMENT` | `ACTIVE`, `CANCELLED`, `IN_ARREARS` | El cliente está en el flujo de checkout. |
| `ACTIVE` | `IN_ARREARS`, `CANCELLED`, `CASE_REPORTED` | Póliza vigente; puede reportar un siniestro. |
| `CASE_REPORTED` | `CASE_IN_PROGRESS`, `CANCELLED` | Se ha iniciado un proceso de asistencia. |

### Lógica de Validación

Cuando se intenta cambiar el estado de una póliza, el sistema ejecuta una validación estricta antes de persistir el cambio en la base de datos:

```python
# app/modules/emission/state_machine.py

def transition(current: PolicyStatus, target: PolicyStatus) -> PolicyStatus:
    # Si el estado destino no está en la lista de permitidos para el estado origen
    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Transición inválida: {current} → {target}")
    return target
```
*Si se intenta pasar de DRAFT a ACTIVE directamente, el sistema lanzará un error de validación, forzando a que la lógica pase siempre por el estado de pago.*

## Ejemplo Práctico: Cambio de Estado tras Pago

```python
# app/modules/emission/service.py

@audited(action="activate_policy", entity="policy")
async def activate_policy(db: AsyncSession, policy_id: uuid.UUID):
    policy = await get_policy(db, policy_id)
    # Validamos y ejecutamos la transición lógica
    new_status = transition(policy.status, PolicyStatus.ACTIVE)
    policy.status = new_status
    await db.commit()
    return policy
```
*Aquí, el servicio de emisión colabora con la FSM para asegurar que la póliza `policy_id` solo se active si su estado actual lo permite.*

## Ciclo de Vida de una Póliza

![State Machine Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844119/251b5468-f7af-4171-9170-d55782e50f17.png)
