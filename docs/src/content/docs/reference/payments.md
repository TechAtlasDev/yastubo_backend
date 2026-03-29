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

### Gestión de Errores y Retintentos
Si un cobro recurrente falla:
*   Stripe notifica mediante `invoice.payment_failed`.
*   Yastubo cambia el estado de la póliza a `IN_ARREARS` (En mora).
*   Se activa el flujo de notificaciones para recordar el pago.
*   Si el pago se regulariza, la póliza vuelve automáticamente a `ACTIVE`.

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

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/payments/one-time` | Procesa un pago único para una póliza. |
| `POST` | `/api/v1/payments/subscribe` | Inicia una suscripción recurrente mensual. |
| `POST` | `/api/v1/payments/webhook` | Endpoint para notificaciones de Stripe. |
| `GET` | `/api/v1/payments/connect/onboarding` | Inicia el flujo de registro de vendedor en Stripe. |
