# Deuda Técnica del Proyecto YASTUBO Backend

**Generado:** 2026-03-28  
**Última actualización:** 2026-03-29 (Estado: Mayoría de ítems críticos resueltos)

---

## Resumen Ejecutivo

El proyecto ha pasado por una fase intensiva de limpieza de deuda técnica. Se han resuelto los errores de ejecución (runtime) y se han implementado lógicas críticas que antes eran mocks.

**Estado actual:**
*   **Errores Críticos:** 0 pendientes.
*   **Lógica de Negocio:** Integrada (Stripe, Zoho, AI History).
*   **Pendientes:** Apple Wallet (Real) y Voice AI Bridge.

---

## 1. Datos Mockeados en Código de Producción

### 1.1 PassbookService — Apple Wallet (`app/modules/emission/passbook_service.py`)
**Estado: PENDIENTE**
(Sin cambios, sigue retornando mock bytes).

### 1.2 Módulo de Voz — WebSocket Bridge (`app/modules/voice/router.py`)
**Estado: PENDIENTE**
(Sin cambios, sigue siendo un stub).

### 1.3 Dashboard — CAC Real (`app/modules/dashboard/service.py`)
**Estado: SOLUCIONADO**
Ahora se calcula como `total_revenue / converted_leads`.

### 1.4 Dashboard — Revenue por Mes (`app/modules/dashboard/service.py`)
**Estado: SOLUCIONADO**
Implementada query SQL con `extract('year/month')` y `group_by`.

### 1.5 Portal Service — Limpieza de Mocks (`app/modules/portal/service.py`)
**Estado: SOLUCIONADO**
Se eliminó la detección de `MagicMock` y se usa el flujo real de Stripe.

### 1.6 Reseller Dashboard — Balance Real (`app/modules/payments/service.py`)
**Estado: SOLUCIONADO**
Ahora consulta la API de Balance de Stripe Connect.

---

## 2. Métodos Invocados Pero No Implementados en StripeClient

### 2.1 `stripe_client.get_payment_method()`
**Estado: SOLUCIONADO** (Implementado en `app/modules/payments/stripe_client.py`).

### 2.2 `stripe_client.get_customer_id_by_email()`
**Estado: SOLUCIONADO** (Implementado en `app/modules/payments/stripe_client.py`).

---

## 3. Configuraciones Ausentes del Modelo de Settings

### 3.1 `N8N_WEBHOOK_URL`
**Estado: SOLUCIONADO** (Agregado a `Settings` en `app/core/config.py`).

### 3.2 Certificados de Apple Wallet
**Estado: SOLUCIONADO** (Migrados al modelo de `Settings`).

---

## 4. Funcionalidades Esqueletizadas

### 4.1 Historial de Chat IA
**Estado: SOLUCIONADO**
Implementada persistencia en `ChatConversation` y `ChatMessage` con contexto de los últimos 10 mensajes.

### 4.2 Ajuste de Facturación Stripe
**Estado: SOLUCIONADO**
Ahora ajusta el `Subscription Item` en Stripe cuando un beneficiario es marcado como fallecido.

### 4.3 Sincronización CRM de Leads
**Estado: SOLUCIONADO**
Integrado en `create_or_update_lead` vía tarea asíncrona hacia Zoho.

### 4.7 `get_or_create_customer` (Duplicados)
**Estado: SOLUCIONADO**
Ahora realiza lookup por email antes de crear.

### 4.8 Tarea de Checkouts Abandonados
**Estado: SOLUCIONADO**
Conectada al worker de ARQ con ejecución cada 6h.

### 4.9 Dashboard — Guard de Workspace
**Estado: SOLUCIONADO**
Añadida validación de `HTTP 404` si el usuario no tiene workspaces.

### 4.10 Templates de Email
**Estado: SOLUCIONADO**
Directorio `notifications/templates/` creado con los archivos correctos.

### 4.11 Normalización E.164
**Estado: SOLUCIONADO**
Añadida validación Pydantic y normalización en `LeadCreate`.

---

## 5. Tabla Resumen de Deuda Técnica

| ID | Módulo | Problema | Tipo | Severidad | Acción Requerida |
|---|---|---|---|---|---|
| DT-01 | `emission/passbook_service.py` | Retorna `b"MOCK_PKPASS_CONTENT_FOR_YASTUBO_V2"` | Dato Mockeado | CRÍTICA | Implementar generación real de `.pkpass` |
| DT-02 | `voice/router.py` | WebSocket media handler es `pass` | Stub vacío | CRÍTICA | Implementar pipeline STT→LLM→TTS→Twilio |
| DT-03 | `portal/service.py` | Método `get_payment_method()` inexistente en `StripeClient` | Método ausente | CRÍTICA | Agregar método a `StripeClient` |
| DT-04 | `portal/service.py` | Método `get_customer_id_by_email()` inexistente en `StripeClient` | Método ausente | CRÍTICA | Agregar método a `StripeClient` |
| DT-05 | `core/events.py` + `config.py` | `N8N_WEBHOOK_URL` no está en Settings; todos los eventos se descartan | Config ausente | ALTA | Agregar campo al modelo `Settings` |
| DT-06 | `payments/service.py` | `get_or_create_customer()` siempre crea un nuevo customer en Stripe | Lógica incorrecta | ALTA | Implementar lookup por email/ID antes de crear |
| DT-07 | `ai/service.py` | Historial de chat no persiste; `ChatConversation`/`ChatMessage` nunca usados | TODO pendiente | ALTA | Implementar gestión de historial |
| DT-08 | `emission/service.py` | `billing_adjustment_confirmed = True` sin ajuste real en Stripe | Confirmación falsa | ALTA | Ajustar suscripción en Stripe antes de confirmar |
| DT-09 | `leads/` + `crm/` | Leads no se sincronizan con Zoho; `zoho_lead_id` siempre `None` | Feature ausente | ALTA | Implementar sync de Lead → Zoho |
| DT-10 | Alembic migrations | Sin migración para módulos `ai` y `leads` (pgvector no activado) | Migración faltante | ALTA | Crear migraciones + activar extensión pgvector |
| DT-11 | `notifications/email_service.py` | Templates de email no existen en la ruta que busca `EmailService` | Config de ruta | ALTA | Crear directorio `notifications/templates/` con los templates |
| DT-12 | `dashboard/service.py` | CAC hardcodeado a `$15.00` (dato mockeado) | Dato Mockeado | MEDIA | Implementar cálculo real o input manual |
| DT-13 | `dashboard/service.py` | `revenue_by_month={}` es placeholder vacío | Placeholder | MEDIA | Implementar query SQL agrupada por mes |
| DT-14 | `portal/service.py` | Lógica de detección de `MagicMock` en código de producción | Código de tests mezclado | MEDIA | Limpiar lógica, acceder directamente al dict de Stripe |
| DT-15 | `payments/service.py` | `pending_commissions: 0.0` hardcodeado | Dato Mockeado | MEDIA | Consultar Balance API de Stripe Connect |
| DT-16 | `leads/tasks.py` | `check_abandoned_checkouts` no wired al worker ARQ | Feature desconectada | MEDIA | Agregar tarea a `WorkerSettings` |
| DT-17 | `dashboard/router.py` | Acceso a `workspaces[0]` sin guard (potencial `IndexError`) | Bug latente | MEDIA | Agregar validación antes del acceso |
| DT-18 | `emission/models.py` + `crm/` | `zoho_beneficiary_id` y `zoho_subscription_id` nunca poblados | Feature ausente | MEDIA | Implementar sync de Beneficiary/Subscription → Zoho |
| DT-19 | `crm/mapper.py` | Mapper solo mapea 6 campos básicos de Contact y Deal | Mapper incompleto | MEDIA | Extender mapper con campos de retención, atribución, etc. |
| DT-20 | `leads/schemas.py` | `phone_e164` no valida formato E.164 (solo es un `str`) | Validación ausente | MEDIA | Agregar validador Pydantic con normalización E.164 |
| DT-21 | `emission/passbook_service.py` + `config.py` | `APPLE_PASS_CERT_PATH/KEY_PATH` fuera del modelo Settings | Config inconsistente | BAJA | Mover a `Settings` |

---

## 6. Priorización Recomendada

### Sprint Inmediato (Bloqueos de Producción)

Los siguientes ítems **rompen en runtime** y deben resolverse antes de cualquier despliegue:

1. **DT-03** y **DT-04** → Métodos faltantes en `StripeClient` (crashean endpoints del portal)
2. **DT-11** → Templates de email en ruta incorrecta (crashea todo envío de email cuando habilitado)
3. **DT-10** → Migraciones faltantes (base de datos sin tablas del módulo AI y posible FK rota)
4. **DT-05** → `N8N_WEBHOOK_URL` en Settings (event-driven architecture completamente deshabilitada)

### Sprint Corto (Calidad de Datos e Integridad)

5. **DT-06** → Duplicados en Stripe (problema que crece con cada pago)
6. **DT-08** → Confirmación falsa de ajuste de facturación por fallecimiento
7. **DT-14** → Código de tests en producción (riesgo de comportamiento inesperado)
8. **DT-17** → Guard en acceso al workspace del dashboard

### Mediano Plazo (Funcionalidades Críticas del Negocio)

9. **DT-07** → Historial de chat IA
10. **DT-09** + **DT-18** → Sincronización completa con Zoho (Leads, Beneficiaries, Subscriptions)
11. **DT-12** + **DT-13** + **DT-15** → KPIs reales en el dashboard
12. **DT-16** → Wiring del task de checkouts abandonados
13. **DT-20** → Normalización E.164

### Largo Plazo (Funcionalidades Nuevas)

14. **DT-01** → Apple Wallet real
15. **DT-02** → Voice AI bridge completo
16. **DT-19** → Mapper CRM completo
17. **DT-21** → Consolidación de Settings

---

*Este documento refleja el estado del código en la rama analizada. Debe actualizarse conforme se resuelvan los ítems identificados.*
