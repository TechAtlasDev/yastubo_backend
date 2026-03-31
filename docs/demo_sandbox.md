# Guía de Demo y Sandbox (Stripe)

Esta guía explica cómo probar el flujo completo de pagos y la gestión de siniestros utilizando el modo Sandbox de Stripe y el CLI oficial.

## 1. Configuración del Stripe CLI

Para recibir webhooks en tu entorno local:

1.  [Instala el Stripe CLI](https://stripe.com/docs/stripe-cli).
2.  Inicia sesión:
    ```bash
    stripe login
    ```
3.  Redirige los webhooks al backend de Yastubo:
    ```bash
    stripe listen --forward-to localhost:8000/api/v1/payments/webhook
    ```
    Copia el `signing secret` (`whsec_...`) y configúralo en tu archivo `.env` como `STRIPE_WEBHOOK_SECRET`.

## 2. Flujo de Prueba de Idempotencia

La idempotencia asegura que si Stripe reintenta enviar un evento (ej. por un error temporal de red), Yastubo no procesará el mismo cobro dos veces.

### Escenario: Pago Exitoso Reintentado

1.  Realiza una compra de una póliza en el portal.
2.  Observa el evento `payment_intent.succeeded` en la terminal donde corre `stripe listen`.
3.  Para simular un reintento manual del mismo evento:
    ```bash
    stripe events resend <ID_DEL_EVENTO_ANTERIOR>
    ```
4.  Verifica los logs del backend. Deberías ver:
    `INFO | app.modules.payments.webhook_handler:handle_stripe_event:25 - Stripe event evt_... already processed. Skipping.`

## 3. Pruebas de Siniestros (Claims)

Puedes disparar el flujo de siniestros directamente desde la API o mediante el CLI de gestión.

### Paso a paso:

1.  **Emitir Póliza:** Usa el portal o la API para crear una póliza activa.
2.  **Reportar Siniestro:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/claims/ \
      -H "Authorization: Bearer <JWT_TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{
        "policy_id": "<POLICY_ID>",
        "beneficiary_id": "<BENEFICIARY_ID>",
        "description": "Siniestro de prueba"
      }'
    ```
3.  **Aprobar Siniestro:** Cambia el estado a `APPROVED`. Esto disparará el Worker asíncrono que marcará al beneficiario como `deceased`.
4.  **Verificar Beneficiario:** Consulta la póliza y verifica que el beneficiario tiene `deceased_flag: true`.

## 4. Analítica en Tiempo Real

Después de aprobar siniestros y registrar gastos, consulta el Dashboard:
- `GET /api/v1/dashboard/metrics`
- Verifica que el **Loss Ratio** se actualice dinámicamente:
  `Loss Ratio = (Gastos Totales de Siniestros / Ingresos Totales del Company) * 100`
