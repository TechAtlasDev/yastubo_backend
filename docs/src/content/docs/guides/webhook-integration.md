---
title: Integración de Webhooks
description: Cómo manejar eventos asíncronos externos (Stripe) de manera segura y robusta.
---

# Integración de Webhooks (Stripe)

Los webhooks permiten a Yastubo reaccionar a eventos que ocurren fuera de su sistema, como pagos exitosos, fallos de cobro o cancelaciones de suscripciones en Stripe. El sistema utiliza una arquitectura asíncrona e idempotente para asegurar que cada evento se procese exactamente una vez.

## Core Benefits / Key Features
* **Procesamiento Idempotente:** Garantizamos que el mismo evento no se procese dos veces gracias al registro de `StripeEvent`.
* **Seguridad de Firma:** Verificación automática de firmas para evitar ataques de suplantación.
* **Transiciones de Estado Automáticas:** La póliza cambia de estado (ej. `ACTIVE`, `IN_ARREARS`) según los eventos de pago.
* **Conversión de Leads:** Los prospectos se convierten automáticamente en clientes finales tras el primer pago exitoso.

## Deep Dive Técnico: Manejo de Eventos

El controlador principal reside en `app/modules/payments/webhook_handler.py`. 

### Lógica de Procesamiento Segura

El flujo de trabajo para cada webhook recibido sigue estos pasos:

1. **Chequeo de Idempotencia:** Buscamos el ID del evento en nuestra base de datos. Si ya existe, abortamos.
2. **Despacho por Tipo:** Dependiendo del `event_type`, delegamos a una lógica específica.
3. **Persistencia de Evento:** Al finalizar con éxito, marcamos el evento como procesado.

```python
# Lógica clave de idempotencia en handle_stripe_event
res = await db.execute(select(StripeEvent).where(StripeEvent.event_id == event_id))
if res.scalar_one_or_none():
    logger.info(f"Stripe event {event_id} ya procesado. Ignorando.")
    return
```

### Eventos Principales Soportados

| Evento | Acción en Yastubo |
| :--- | :--- |
| `payment_intent.succeeded` | Marca la transacción como exitosa y activa la póliza. |
| `payment_intent.payment_failed` | Incrementa el contador de intentos y notifica al cliente. |
| `customer.subscription.deleted` | Cancela la suscripción y cambia la póliza a estado `CANCELLED`. |
| `invoice.payment_succeeded` | Registra el pago recurrente de una suscripción activa. |

## Ejemplo Práctico: Añadir un Nuevo Evento

Si deseas manejar el evento `charge.refunded` para gestionar reembolsos automáticos:

```python
# app/modules/payments/webhook_handler.py

elif event_type == "charge.refunded":
    charge_id = data_obj.get("id")
    # Lógica para marcar transacción como reembolsada
    await process_refund(db, charge_id)
    
    # Registrar el evento procesado
    db.add(StripeEvent(event_id=event_id, event_type=event_type))
    await db.commit()
```

:::note[Seguridad]
Aunque el ejemplo de código muestra el procesamiento del objeto `event`, en producción la validación de la firma de Stripe ocurre en la capa del router antes de llamar al controlador.
:::

## Diagrama de Ciclo de Vida de Webhook

![Webhook Integration Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844516/055773c8-4ba1-4d37-a8b1-033689e7a1cb.png)
