---
title: Historial de Lanzamientos (Releases)
description: Registro de cambios y mejoras arquitectónicas del backend de Yastubo.
---

## [0.4.0] - 2026-03-30

### Añadido
- **Motor de Reintentos de Cobro**: Nuevo endpoint `POST /api/v1/payments/transactions/{id}/retry` con límite configurable de `MAX_PAYMENT_ATTEMPTS = 2`. Al primer y segundo intento crea un nuevo `PaymentIntent` en Stripe. Al alcanzar el límite, bloquea el reintento y dispara `on_payment_failed()` que notifica al cliente automáticamente por **email y WhatsApp** para que actualice su método de pago.
- **Schema `RetryPaymentResponse`**: Contrato de respuesta con `transaction_id`, `attempt_count`, `status`, `message` y `client_secret`.
- **Tests de Reintentos (5 casos)**: Cobertura completa del nuevo endpoint:
  - Primer reintento exitoso (`attempt_count` 1 → 2, status `PENDING`)
  - Bloqueo al alcanzar el límite (HTTP 422 + notificación al cliente)
  - Rechazo de transacciones no-`FAILED`
  - 404 para ID inexistente
  - 401 sin autenticación
- **Guía de Despliegue en VPS** (`docs/guides/deployment`): Guía paso a paso para Ubuntu 22.04 con Docker Compose. Incluye preparación del servidor, configuración de `.env`, ejecución de migraciones, health check, Nginx como reverse proxy con soporte WebSocket (Voice AI), configuración de webhooks Stripe y tabla de solución de problemas.

### Solucionado
- **`docker-compose.yml`**: La dependencia `depends_on` del servicio `app` referenciaba `mysql` (servicio inexistente) en lugar de `postgres`. El stack no podía levantarse. Corregido.
- **`.env.example`**: Archivo incompleto — se añaden `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (requeridas por docker-compose), `APPLE_PASS_CERT_PATH` y `APPLE_PASS_KEY_PATH`. Cada variable ahora incluye comentario explicativo y URL de referencia para facilitar el onboarding.

### Mejoras
- **Documentación de Payments**: Tabla completa de endpoints con roles requeridos, tabla de comportamiento de reintentos por intento y ejemplos de respuesta HTTP con tip de notificación automática.

---

## [0.3.0] - 2026-03-29

### Añadido
- **Módulo AI (Historial & RAG)**: Persistencia de conversaciones (`ChatConversation`) y mensajes (`ChatMessage`) con contexto multi-turno (últimos 10 mensajes) para Gemini.
- **Sincronización Zoho Leads**: Los prospectos creados/actualizados se sincronizan automáticamente con Zoho CRM de forma asíncrona.
- **Ajuste de Suscripción Stripe**: Implementación real de `update_subscription_item_price` en `StripeClient`, activada automáticamente al marcar un beneficiario como fallecido.
- **Normalización E.164**: Validación y normalización automática de teléfonos en el módulo de Leads usando Pydantic.
- **Testing**: Nueva suite de pruebas de integración (`tests/test_debt_fixes.py`) para verificar Stripe, AI History y Zoho Sync.

### Solucionado (Deuda Técnica Crítica)
- **StripeClient**: Implementación de métodos faltantes `get_payment_method` y `get_customer_id_by_email`.
- **Detección de Duplicados**: `get_or_create_customer` ahora realiza lookup por email antes de crear en Stripe.
- **Email Templates**: Corrección de rutas de carga de plantillas en `notifications/email_service.py`.
- **Seguridad Dashboard**: Validación de existencia de workspace para evitar `IndexError`.
- **Configuración**: Registro de `N8N_WEBHOOK_URL` y certificados Apple en el modelo centralizado de `Settings`.
- **Worker**: Conexión de la tarea de "Checkouts Abandonados" al worker de ARQ.

### Mejoras
- **Dashboard de KPIs**: CAC y Revenue por Mes ahora utilizan datos reales de transacciones y leads en lugar de valores hardcodeados.
- **Limpieza de Código**: Eliminación de lógica de detección de `MagicMock` en código de producción del portal.

---

## [0.2.0] - 2026-03-26

### Añadido
- **Módulo de Planes**: Se han incorporado campos de "Periodos de Espera" (*Vesting Periods*) al modelo de `Plan` para automatizar la validación de derechos de asistencia.
    - `vesting_accidental_days`: Días de espera para muerte accidental (por defecto 0).
    - `vesting_natural_days`: Días de espera para muerte natural (por defecto 180).
    - `vesting_suicide_days`: Días de espera para suicidio (por defecto 365).
- **Esquemas de API**: Actualización de los esquemas Pydantic `PlanCreate`, `PlanUpdate` y `PlanResponse` para incluir los nuevos campos.
- **Carga Masiva (Stretch)**: Implementación de `POST /emission/bulk-upload` para cargar beneficiarios vía Excel (Pandas).
- **Dashboard de KPIs (Stretch)**: Nuevo módulo `dashboard` con métricas de negocio en tiempo real (LTV, CAC, Churn, MRR, Atribución por Canal).
- **Migraciones**: Nueva revisión de Alembic (`ecb513a9360b`) para actualizar la tabla `plans`.

### Mejoras
- **Capacidad de Soporte**: El sistema ahora es totalmente compatible con la lógica multinacional de planes como "de Ahorita y Siempre" y "Yastubo de Pe a Pa", permitiendo una validación programática de la carencia sin intervención humana.

---

## [0.1.0] - 2026-03-19

### Añadido
- Versión inicial del backend modular.
- Módulos de Autenticación, Planes, Emisiones y Pagos (Stripe).
- Integración básica con IA (Gemini).
