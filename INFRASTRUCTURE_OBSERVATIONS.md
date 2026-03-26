# Observaciones de Infraestructura y Aptitud Técnica - Yastubo Backend

Este documento centraliza el análisis de la arquitectura actual frente a las especificaciones de negocio de Yastubo.

## 1. Análisis de Aptitud del Proyecto (Monolito Modular FastAPI)

| Requisito | Estado | Observación Técnica |
| :--- | :---: | :--- |
| **Backend como Fuente de Verdad** | ✅ Apto | Estructura modular sólida (`plans`, `payments`, `emission`). Los modelos centralizan la lógica de suscripción. |
| **Precio Individual por Beneficiario** | ✅ Apto | Soportado por la lógica en `app/modules/plans/calculator.py`. |
| **Integración Zoho CRM (Snapshots)** | ⚠️ Parcial | Existe `zoho_client.py`. Sin embargo, el backend actual solo soporta una relación 1:1 entre Póliza y Cliente. Falta el soporte para múltiples beneficiarios (Beneficiary Snapshots) y el módulo de Suscripción (Subscription Snapshot). |
| **Módulo de Leads (Pre-compra)** | ❌ Ausente | No existe un modelo de datos ni lógica para capturar prospectos (Leads) con sus datos de atribución (UTMs, campañas) antes de la creación de la póliza/cliente. |
| **Precio Individual x Beneficiario** | ⚠️ Parcial | La calculadora permite calcular precios individuales (`calculator.py`), pero el modelo de `Policy` solo almacena un único `insured_age` y un `final_price` total, sin desglosar beneficiarios. |

## 2. Puntos Críticos Identificados

1. **Estructura 1:1 vs 1:N (Beneficiarios):** El backend asume que un `Client` es el único asegurado de la `Policy`. Yastubo requiere que una Suscripción (vinculada a un pagador/contacto) tenga múltiples Beneficiarios, cada uno con su propio Snapshot en Zoho y su propio flag de `deceased_flag`.
2. **Falta de Atribución en Leads:** No hay campos para `utm_source`, `campaign_id`, `adset_id`, etc., necesarios para la capa comercial y de marketing en Zoho.
3. **Flujo de Checkout Abandonado:** El sistema debe capturar datos de intención de compra para crear un `Lead` en Zoho antes de que Stripe confirme el pago. Actualmente, el flujo parece centrado en la confirmación exitosa (`webhook_handler.py`).
4. **Espejo de Suscripción:** Los campos de solo lectura en Zoho (MRR, fecha de renovación, conteo de beneficiarios) deben ser calculados y empujados por el backend, pero actualmente no existen todos estos campos en el modelo `Subscription`.

## 4. Propuesta de Esquema de Base de Datos EXHAUSTIVO

Para que el Backend sea la Fuente de Verdad, debe almacenar el 100% de los campos que el CRM consumirá.

### A. Tabla: `leads` (Prospectos)
- **Identidad:** `id` (UUID), `first_name`, `last_name`, `phone_e164` (Matching key), `phone_raw`, `email`, `preferred_language`, `country_of_residence`, `nationality`, `city`, `state_region`.
- **Atribución:** `source_channel`, `campaign_name`, `campaign_id`, `adset_id`, `ad_id`, `utm_source`, `utm_medium`, `utm_campaign`, `landing_page`, `referral_source`.
- **Comercial:** `lead_status` (Enum), `funnel_stage` (Enum), `lead_score` (Int), `intent_level` (Enum).
- **Conversación:** `first_contact_at`, `last_conversation_at`, `last_conversation_channel`, `conversation_status`, `whatsapp_opt_in_status`, `chatwoot_contact_id`, `chatwoot_conversation_id_last`, `assigned_agent`, `ai_handled_flag`, `human_handoff_flag`, `last_message_summary`.
- **Checkout:** `form_started` (Bool), `form_completed` (Bool), `checkout_started` (Bool), `checkout_started_at`, `checkout_completed` (Bool), `abandoned_checkout_flag` (Bool), `abandoned_checkout_at`, `purchase_completed` (Bool).
- **Seguimiento:** `followup_whatsapp_sent` (Bool), `followup_whatsapp_sent_at`, `followup_sequence_step` (Int), `next_followup_at`, `converted_to_contact_flag` (Bool), `converted_at`.

### B. Tabla: `clients` (Contacts)
- **Identidad:** `backend_customer_id` (PK técnica), `first_name`, `last_name`, `phone_e164`, `email`, `preferred_language`, `country_of_residence`, `customer_since`, `acquisition_channel`, `campaign_name`.
- **Retención:** `churn_risk_level`, `collections_risk_level`, `last_failed_payment_at`, `retention_sequence_status`, `winback_eligible_flag`.
- **Conversación:** `last_conversation_at`, `chatwoot_contact_id`.

### C. Tabla: `subscriptions` (Subscription Snapshot)
- **Identidad:** `backend_subscription_id` (PK), `plan_name`, `plan_code`.
- **Finanzas:** `monthly_price`, `currency`, `billing_frequency`, `mrr_snapshot`.
- **Estado:** `status` (Active, Paused, etc.), `payment_status` (Current, Failed, Overdue), `failed_payment_count`, `beneficiaries_count`.
- **Fechas:** `subscription_created_at`, `subscription_activated_at`, `renewal_date`, `last_payment_date`, `next_payment_due_date`.
- **Cancelación:** `cancelled_at`, `cancellation_reason`, `snapshot_last_synced_at`.

### D. Tabla: `beneficiaries` (Beneficiary Snapshot)
- **Identidad:** `backend_beneficiary_id` (PK), `first_name`, `last_name`, `date_of_birth`, `relationship`, `country_of_residence`, `location_type`.
- **Estado:** `coverage_status`, `individual_price`.
- **Excepción Crítica:** `deceased_flag` (Bool), `deceased_reported_at`, `deceased_reported_by`, `backend_api_call_sent`, `backend_api_call_sent_at`, `billing_adjustment_confirmed`.
- **Sincronización:** `snapshot_last_synced_at`.

## 5. Identidad y Reglas de Deduplicación (CRÍTICO)

La integridad del CRM depende de estas reglas de negocio que el Backend debe imponer:

- **Clave Maestra:** `phone_e164` (Formato estricto E.164, ej: `+13475551234`).
- **Normalización:** El backend debe normalizar cada entrada y almacenar el original en `phone_raw` y el procesado en `phone_e164`.
- **Orden de Matching para Sincronización:**
    1. `backend_customer_id` (Prioridad máxima para Contacts).
    2. `phone_e164` (Prioridad para Leads/Contacts).
    3. `email` (Consolidación secundaria).
- **Regla de Oro:** Nunca crear dos registros Lead con el mismo `phone_e164`. Fusionar si hay colisión entre WhatsApp y Webchat.

## 6. Arquitectura de Sincronización y Eventos

El sistema operará bajo un modelo **Event-Driven** orquestado por **n8n**:

### A. Flujo de Entrada (Lead Acquisition)
- **WhatsApp/Webchat/Form:** Evento -> n8n -> CRM (Crear/Actualizar Lead).
- **Checkout Iniciado:** Backend -> n8n -> CRM (`checkout_started = true`).

### B. Flujo de Conversión (Lead -> Contact)
- **Disparador:** Webhook `purchase_completed` del Backend.
- **Acción CRM:** Convertir Lead + Crear Contact + Crear Subscription Snapshot + Crear Beneficiary Snapshots.

### C. El Único Write-Back (CRM -> Backend)
- **Ruta:** `POST /api/v1/beneficiaries/{backend_beneficiary_id}/mark-deceased`
- **Requisitos:** El backend debe validar la llamada, ajustar Stripe, actualizar la DB interna y devolver la confirmación para que Zoho marque `billing_adjustment_confirmed = true`.

## 7. Convenciones de Nomenclatura (Obligatorias)

Para evitar desajustes en la sincronización, todo el código y la base de datos deben seguir:
- **Idioma:** Inglés.
- **Formato:** `snake_case`.
- **Sufijos:** `_at` para timestamps, `_flag` para booleanos.
- **Prefijos:** `backend_` para IDs compartidos con el CRM.

## 8. Análisis de Factibilidad de Infraestructura

Tras revisar los requisitos finales, el proyecto actual es **APTO** mediante las siguientes acciones:
1. **Migración de DB:** Implementar el esquema exhaustivo propuesto en la Sección 4.
2. **Endpoint de Write-Back:** Crear el router específico para la notificación de fallecimiento.
3. **Normalizador de Teléfonos:** Añadir lógica de normalización E.164 en los esquemas de Pydantic.
4. **Emisor de Webhooks:** Extender el módulo `app/modules/payments/webhook_handler.py` para que emita eventos hacia n8n, no solo procesos internos.
