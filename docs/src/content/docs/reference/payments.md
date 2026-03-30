---
title: Payments (Gestión Financiera)
description: Integración con Stripe, pagos recurrentes y gestión de comisiones mediante Connect.
---

El módulo de **Payments** gestiona toda la capa financiera de Yastubo. No solo procesa pagos unitarios y suscripciones, sino que también orquestra la distribución de comisiones a los revendedores (Vendedores) a través de Stripe Connect.

## Key Features

*   **Pagos Unitarios y Suscripciones**: Soporte para cobros de pólizas anuales (un solo pago) o mensuales (recurrente).
*   **Stripe Connect (Custom/Express)**: Onboarding automático para vendedores, permitiendo depósitos directos de comisiones.
*   **Gestión de Comisiones**: Cálculo automático de "Application Fees" que la plataforma retiene antes de enviar el saldo al vendedor.
*   **Webhook Handler**: Sistema robusto de escucha de eventos de Stripe para actualizar el estado de las pólizas y suscripciones en tiempo real.
*   **Reintentos de Cobro Inteligentes**: Motor de reintentos con límite de 2 intentos y notificación automática al cliente vía email + WhatsApp al alcanzar el límite.

:::tip[Stripe Connect]
Yastubo utiliza una arquitectura de pagos indirectos donde el cliente paga al vendedor, y la plataforma retiene una comisión configurable por espacio de trabajo.
:::

## Deep Dive Técnico

### Flujo de Suscripción
Cuando un cliente opta por un plan mensual:
1.  **Customer Creation**: El sistema verifica si el usuario ya existe en Stripe; si no, lo crea.
2.  **Payment Method**: Se vincula el método de pago proporcionado.
3.  **Subscription Link**: Se asocia el `price_id` del plan de Yastubo con la suscripción en Stripe.
4.  **Commission Splitting**: Si el vendedor tiene Connect activo, se aplica el `application_fee_percent` definido en el `Workspace`.

### Gestión de Errores y Reintentos

Si un cobro recurrente falla vía webhook de Stripe:
*   Stripe notifica mediante `invoice.payment_failed`.
*   Yastubo cambia el estado de la póliza a `IN_ARREARS` (En mora).
*   Se activa el flujo de notificaciones para recordar el pago.
*   Si el pago se regulariza, la póliza vuelve automáticamente a `ACTIVE`.

El sistema también soporta **reintentos manuales** desde el panel de administración:

#### Motor de Reintentos (`MAX_PAYMENT_ATTEMPTS = 2`)

| Intento | Comportamiento |
| :--- | :--- |
| 1er reintento | Crea un nuevo `PaymentIntent` en Stripe. La transacción vuelve a `PENDING`. |
| 2do reintento | Último intento permitido. Mismo flujo que el primero. |
| Límite alcanzado | El sistema **bloquea el reintento** y envía notificación automática al cliente por **email y WhatsApp** para que actualice su método de pago. |

```python
# app/modules/payments/service.py

MAX_PAYMENT_ATTEMPTS = 2

async def retry_payment(db, stripe, transaction_id, retried_by):
    # Si se alcanzó el límite: notificar y bloquear
    if transaction.attempt_count >= MAX_PAYMENT_ATTEMPTS:
        await notifications.on_payment_failed(policy, client, transaction.attempt_count)
        raise HTTPException(422, "Maximum retry attempts reached. Client notified.")

    # Crear nuevo PaymentIntent y reintentar
    pi = await stripe.create_payment_intent(...)
    transaction.attempt_count += 1
    transaction.status = "PENDING"
```

### Recordatorios de Pago y Vencimiento
Para pólizas que no utilizan suscripciones recurrentes, el sistema ejecuta tareas diarias para:
1.  **Recordatorios de Mora**: Avisar a clientes con pólizas en `IN_ARREARS`.
2.  **Aviso de Vencimiento**: Notificar 3 días antes de que la vigencia de la póliza termine (`end_date`).

## Ejemplo Práctico: Creación de Suscripción

El siguiente código muestra cómo se orquestra una suscripción con división de comisiones:

```python
async def create_subscription(
    db: AsyncSession,
    stripe: StripeClient,
    data: CreateSubscriptionRequest,
    issued_by: uuid.UUID,
) -> Subscription:
    """
    Crea una suscripción en Stripe vinculada a una póliza.
    Gestiona la división de comisiones si hay un revendedor activo.
    """
    policy = await emission_service.get_policy(db, data.policy_id)
    workspace = await get_workspace(db, policy.workspace_id)

    # Configuración de comisiones para Stripe Connect
    connect_account_id = None
    app_fee_percent = None

    if workspace.is_reseller and workspace.stripe_connect_id:
        connect_account_id = workspace.stripe_connect_id
        app_fee_percent = float(workspace.commission_rate) # Lo que se queda la plataforma

    # 1. Obtener o crear el cliente en Stripe
    customer_id = await get_or_create_customer(stripe, policy.client)

    # 2. Iniciar la suscripción en Stripe
    stripe_sub = await stripe.create_subscription(
        customer_id=customer_id,
        price_id=policy.plan.stripe_price_id,
        payment_method_id=data.stripe_payment_method_id,
        connect_account_id=connect_account_id,
        application_fee_percent=app_fee_percent,
    )

    # 3. Persistir la información localmente
    sub = Subscription(
        policy_id=policy.id,
        stripe_subscription_id=stripe_sub["id"],
        status=stripe_sub["status"].upper()
    )
    db.add(sub)
    await db.commit()
    return sub
```

## Diagrama de Proceso

> [FLOW: El cliente selecciona un plan y proporciona su tarjeta. Yastubo crea un Subscription en Stripe. Stripe procesa el primer pago. Si tiene éxito, Stripe envía un webhook 'invoice.paid'. Yastubo recibe el webhook, marca la transacción como exitosa y activa la póliza. Si el pago falla, la póliza se marca en mora].

## Endpoints Principales

| Método | Ruta | Rol requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/payments/intent` | ADMIN, VENDEDOR | Crea un PaymentIntent (pago único). |
| `POST` | `/api/v1/payments/subscription` | ADMIN, VENDEDOR | Inicia una suscripción recurrente mensual. |
| `POST` | `/api/v1/payments/subscription/cancel` | ADMIN | Cancela una suscripción activa. |
| `POST` | `/api/v1/payments/manual` | ADMIN | Registra un pago manual (fuera de Stripe). |
| `GET` | `/api/v1/payments/transactions` | ADMIN, VENDEDOR | Lista transacciones, filtrable por póliza y estado. |
| `POST` | `/api/v1/payments/transactions/{id}/retry` | ADMIN, VENDEDOR | Reintenta un cobro fallido (máx. 2 intentos). |
| `POST` | `/api/v1/payments/connect/onboarding` | Autenticado | Inicia el flujo de registro de vendedor en Stripe Connect. |
| `GET` | `/api/v1/payments/reseller/dashboard` | ADMIN, VENDEDOR | Dashboard de comisiones del revendedor. |
| `POST` | `/api/v1/payments/webhook` | — | Endpoint para notificaciones de Stripe (firma verificada). |

### Ejemplo: Reintentar un cobro fallido

```http
POST /api/v1/payments/transactions/{transaction_id}/retry
Authorization: Bearer <admin_token>
```

**Respuesta exitosa (intento 1 o 2):**

```json
{
  "transaction_id": "uuid",
  "attempt_count": 2,
  "status": "PENDING",
  "message": "Retry attempt 2 of 2 initiated.",
  "client_secret": "pi_xxx_secret_yyy"
}
```

**Respuesta al alcanzar el límite (HTTP 422):**

```json
{
  "detail": "Maximum retry attempts (2) reached. A payment update notification has been sent to the client."
}
```

:::tip[Notificación automática]
Al alcanzar el límite de reintentos, el sistema dispara automáticamente `on_payment_failed` que envía email de recordatorio **y** mensaje de WhatsApp al cliente solicitando actualización del método de pago.
:::
