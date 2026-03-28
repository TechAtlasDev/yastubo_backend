# Deuda Técnica del Proyecto YASTUBO Backend

**Generado:** 2026-03-28  
**Responsable del análisis:** Arquitecto de Software (GitHub Copilot Agent)  
**Metodología:** Revisión exhaustiva de todos los archivos `.py` del proyecto mediante búsqueda de patrones: `TODO`, `FIXME`, `MOCK`, `mock`, `placeholder`, `pass` (sentencias vacías), comentarios de fase/MVP y análisis de coherencia funcional cruzada entre módulos.

---

## Resumen Ejecutivo

El proyecto cuenta con una arquitectura modular sólida y correctamente estructurada. Sin embargo, durante el análisis se identificaron **cuatro categorías** de deuda técnica que comprometen la operabilidad en producción:

1. **Datos y respuestas mockeadas** devueltas por funciones de producción.
2. **Métodos invocados pero no implementados** en la capa de cliente de Stripe.
3. **Configuraciones ausentes** en el modelo de Settings que inutilizan integraciones.
4. **Funcionalidades críticas esqueletizadas** (modelos y scaffolding listos, lógica real ausente).

---

## 1. Datos Mockeados en Código de Producción

### 1.1 PassbookService — Apple Wallet (`app/modules/emission/passbook_service.py`)

**Severidad: CRÍTICA**

```python
# Línea 31
return b"MOCK_PKPASS_CONTENT_FOR_YASTUBO_V2"
```

El método `generate_policy_pass()` está documentado explícitamente como MVP con datos falsos:

> *"For this MVP and test, we return a mock bytes content."*

La integración real con Apple Wallet (generación de archivos `.pkpass` firmados con certificados del Apple Developer Program) **no existe**. Cualquier endpoint que consuma este servicio devuelve bytes inútiles al cliente.

**Impacto:** Funcionalidad de Wallet/Passbook completamente inoperativa en producción.  
**Qué falta:** Implementar la generación real usando una librería como `passkit-generator` o equivalente en Python, configurar los certificados (`APPLE_PASS_CERT_PATH`, `APPLE_PASS_KEY_PATH`) en el modelo de Settings y firmar el `.pkpass` con los datos reales de la póliza.

---

### 1.2 Módulo de Voz — WebSocket Bridge (`app/modules/voice/router.py`)

**Severidad: CRÍTICA**

```python
# Líneas 31-44
elif data["event"] == "media":
    # Twilio sends media as base64 encoded mulaw 8000Hz
    data["media"]["payload"]
    # In a real RAG-Voice scenario, we would:
    # 1. Accumulate audio chunks
    # 2. Use VAD (Voice Activity Detection)
    # 3. Use Whisper/Gemini for STT
    # 4. Use AI Service for response
    # 5. Use ElevenLabs for TTS
    # 6. Send back to Twilio

    # MOCK RESPONSE (For MVP Phase 4 structure)
    # We'll implement the actual bridge logic here
    pass
```

El WebSocket que recibe el audio de Twilio en tiempo real **no hace absolutamente nada**. El comentario describe el pipeline completo (VAD → STT → LLM → TTS → Twilio), pero la implementación es una sentencia `pass`. El payload de audio es leído y descartado silenciosamente.

**Impacto:** El módulo de Voz IA es inoperativo. La inicialización del cliente ElevenLabs sí ocurre en el startup, consumiendo recursos innecesariamente.  
**Qué falta:** Implementar el pipeline completo de voz: acumulación de chunks de audio, integración de VAD, STT (Whisper o Gemini Speech), llamada al AI Service con contexto RAG, síntesis de voz con ElevenLabs y envío del audio de vuelta a Twilio.

---

### 1.3 Dashboard — CAC Mockeado (`app/modules/dashboard/service.py`)

**Severidad: MEDIA**

```python
# Líneas 68-70
# 6. CAC Average (Mock for now, as we don't have ad spend in DB)
# Recommended: Assume $15 USD CAC as default baseline for the machine
cac_average = Decimal("15.00")
```

El indicador de Costo de Adquisición de Clientes (CAC) está hardcodeado a `$15.00 USD` para todos los workspaces. No refleja ningún dato real.

**Impacto:** KPI clave del negocio muestra siempre el mismo valor ficticio, inutilizando la toma de decisiones basada en este dato.  
**Qué falta:** Persistir el gasto en publicidad en la base de datos (ej. integrando datos de Meta/Google Ads) o como campo configurable por workspace. Alternativamente, exponer el campo para entrada manual por período.

---

### 1.4 Dashboard — Revenue por Mes Vacío (`app/modules/dashboard/service.py`)

**Severidad: MEDIA**

```python
# Línea 101
revenue_by_month={},  # Placeholder for grouping
```

El campo `revenue_by_month` del schema `DashboardKPIMetrics` siempre retorna un diccionario vacío. La query SQL para agrupar transacciones por mes nunca fue implementada.

**Impacto:** El gráfico de tendencia de ingresos del dashboard no puede renderizarse con datos reales.  
**Qué falta:** Implementar una query SQL con `GROUP BY` por mes sobre la tabla `transactions` filtrando por `workspace_id` y `status = 'SUCCEEDED'`.

---

### 1.5 Portal Service — Fallback a ID Mockeado (`app/modules/portal/service.py`)

**Severidad: MEDIA**

```python
# Líneas 177-185
pi_id = "pi_mock"
if hasattr(pi, "get") and not hasattr(pi, "assert_called"):
    pi_id = pi.get("id", "pi_mock")
elif hasattr(pi, "status") and not hasattr(pi.status, "assert_called"):
    pi_id = pi.status
    pi_id = getattr(pi, "id", "pi_mock")
```

El código de producción usa detección de `MagicMock` de tests (`hasattr(pi, "assert_called")`) para decidir cómo interpretar la respuesta de Stripe. Si Stripe devuelve una respuesta inesperada, `stripe_payment_intent_id` se guarda como `"pi_mock"` en la base de datos.

**Impacto:** Transacciones reales pueden quedar registradas con IDs ficticios, rompiendo la conciliación con Stripe y el webhook handler.  
**Qué falta:** Limpiar la lógica: acceder directamente al dict de respuesta de Stripe sin lógica de detección de mocks. Los mocks deben resolverse solo en el entorno de tests.

---

### 1.6 Reseller Dashboard — Comisiones Pendientes Hardcodeadas (`app/modules/payments/service.py`)

**Severidad: BAJA-MEDIA**

```python
# Línea ~328
"pending_commissions": 0.0,  # Stripe Connect handles payouts automatically or we can query Stripe Balance
```

Las comisiones pendientes siempre devuelven `0.0`. El comentario reconoce que debería consultarse el Balance de Stripe Connect pero nunca se implementó.

**Impacto:** Los revendedores ven siempre `$0.00` en comisiones pendientes, haciendo inútil el dashboard para ellos.  
**Qué falta:** Consultar la API de Stripe Connect (`stripe.Balance.retrieve(stripe_account=connect_account_id)`) para obtener el balance real del account del revendedor.

---

## 2. Métodos Invocados Pero No Implementados en StripeClient

### 2.1 `stripe_client.get_payment_method()` — No Existe (`app/modules/portal/service.py:100`)

**Severidad: CRÍTICA (rompe en runtime)**

```python
# portal/service.py, línea 100
stripe_pm = await stripe_client.get_payment_method(stripe_pm_id)
```

Este método es invocado en `add_payment_method()` del portal pero **no está definido** en la clase `StripeClient` (`app/modules/payments/stripe_client.py`). La llamada causará un `AttributeError` en runtime.

**Métodos definidos actualmente en StripeClient:** `create_customer`, `create_payment_intent`, `confirm_payment_intent`, `create_subscription`, `cancel_subscription`, `create_connect_account`, `create_account_link`, `construct_webhook_event`.

**Impacto:** El endpoint `POST /portal/payment-methods` falla en producción con error 500.  
**Qué falta:** Implementar `async def get_payment_method(self, pm_id: str) -> dict` wrapeando `stripe.PaymentMethod.retrieve(pm_id)`.

---

### 2.2 `stripe_client.get_customer_id_by_email()` — No Existe (`app/modules/portal/service.py:160`)

**Severidad: CRÍTICA (rompe en runtime)**

```python
# portal/service.py, línea 160
customer_id = await stripe_client.get_customer_id_by_email(client.email)
```

Este método es llamado en `pay_pending_policy()` del portal pero **tampoco existe** en `StripeClient`.

**Impacto:** El endpoint `POST /portal/policies/{policy_id}/pay` falla en producción con error 500.  
**Qué falta:** Implementar `async def get_customer_id_by_email(self, email: str) -> Optional[str]` consultando `stripe.Customer.list(email=email, limit=1)`.

---

## 3. Configuraciones Ausentes del Modelo de Settings

### 3.1 `N8N_WEBHOOK_URL` No Registrado (`app/core/config.py` + `app/core/events.py`)

**Severidad: ALTA**

```python
# core/events.py, línea 15
webhook_url = getattr(settings, "N8N_WEBHOOK_URL", None)

if not webhook_url:
    logger.warning(f"N8N_WEBHOOK_URL not configured. Skipping event: {event_type}")
    return False
```

El módulo `core/events.py` usa `getattr` con fallback `None` porque `N8N_WEBHOOK_URL` **no está declarado en la clase `Settings`** de `config.py`. Resultado: todos los eventos del sistema (`LEAD_CREATED`, `LEAD_UPDATED`, `BENEFICIARY_DECEASED`) nunca se despachan a n8n, aunque el campo esté en el `.env`.

**Módulos afectados:**
- `app/modules/leads/service.py` → eventos `LEAD_CREATED` y `LEAD_UPDATED`
- `app/modules/emission/service.py` → evento `BENEFICIARY_DECEASED`

**Impacto:** La arquitectura event-driven hacia n8n (que debería disparar flujos de CRM, WhatsApp y retargeting) está completamente deshabilitada.  
**Qué falta:** Agregar `N8N_WEBHOOK_URL: str = ""` al modelo `Settings` en `config.py` y verificar el envío con una clave no vacía.

---

### 3.2 Certificados de Apple Wallet Fuera del Modelo de Settings (`app/modules/emission/passbook_service.py`)

**Severidad: BAJA** (bloquea la funcionalidad cuando se implemente)

```python
# passbook_service.py, líneas 13-14
self.cert_path = os.getenv("APPLE_PASS_CERT_PATH")
self.key_path = os.getenv("APPLE_PASS_KEY_PATH")
```

Las rutas a los certificados se leen directamente con `os.getenv()` en lugar de usar el modelo `Settings` centralizado. Esto evita la validación de configuración al startup y es inconsistente con el patrón del proyecto.

**Qué falta:** Agregar `APPLE_PASS_CERT_PATH: str = ""` y `APPLE_PASS_KEY_PATH: str = ""` al modelo `Settings`.

---

## 4. Funcionalidades Esqueletizadas (Modelos Listos, Lógica Ausente)

### 4.1 Historial de Chat IA No Persistido (`app/modules/ai/`)

**Severidad: ALTA**

```python
# ai/service.py, línea 65
# TODO: Implement full history management
```

Los modelos `ChatConversation` y `ChatMessage` están definidos en `ai/models.py` pero **nunca son usados en ningún punto del código**. Cada invocación a `POST /ai/chat` construye el prompt desde cero sin contexto histórico. El contexto conversacional se pierde completamente entre requests.

**Impacto:** El chatbot no tiene memoria. Los usuarios deben repetir contexto en cada mensaje. El modelo está diseñado para conversaciones multi-turno pero funciona como una pregunta/respuesta aislada.  
**Qué falta:** En `chat_with_context()`:
1. Buscar o crear un registro `ChatConversation` por `session_id`.
2. Guardar cada mensaje entrante como `ChatMessage(role="user")`.
3. Recuperar el historial reciente para incluirlo en el prompt.
4. Guardar la respuesta del LLM como `ChatMessage(role="assistant")`.

**Nota adicional:** No existe una migración de Alembic para las tablas `knowledge_documents`, `chat_conversations` y `chat_messages`. Tampoco se valida que la extensión `pgvector` esté habilitada en la DB antes de operar.

---

### 4.2 Ajuste de Facturación por Fallecimiento de Beneficiario No Real (`app/modules/emission/service.py`)

**Severidad: ALTA**

```python
# emission/service.py, líneas 434-436
# Trigger billing adjustment logic (Integration with Stripe would go here)
# For Phase 3, we mark it and notify n8n/Zoho
beneficiary.billing_adjustment_confirmed = True  # Assume confirmed for now
```

El endpoint `mark_beneficiary_deceased()` marca automáticamente `billing_adjustment_confirmed = True` **sin realizar ningún ajuste real en Stripe**. El comentario reconoce explícitamente que "la integración con Stripe iría aquí". El campo está diseñado para ser `True` solo cuando Stripe confirme el ajuste de monto, pero se establece como si ya hubiera ocurrido.

**Impacto:** Se cobra el monto completo al cliente aunque un beneficiario haya fallecido. La suscripción de Stripe no se modifica.  
**Qué falta:**
1. Recalcular el precio de la póliza excluyendo al beneficiario fallecido.
2. Actualizar el `Subscription Item` en Stripe con el nuevo precio.
3. Solo setear `billing_adjustment_confirmed = True` tras la confirmación de Stripe.

---

### 4.3 Sincronización CRM de Leads — Zoho Lead ID Nunca Poblado (`app/modules/leads/`)

**Severidad: ALTA**

El modelo `Lead` tiene el campo:

```python
zoho_lead_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

Sin embargo, **no existe ninguna función** en `crm/service.py`, `crm/mapper.py` ni `leads/service.py` que sincronice leads con Zoho CRM. El campo `zoho_lead_id` siempre será `None`.

**Módulos de CRM actuales:** Solo sincronizan `Client` (como Zoho Contact) y `Policy` (como Zoho Deal). Los leads pre-compra quedan fuera del CRM.

**Impacto:** El equipo comercial no puede ver prospectos en Zoho hasta que convierten, perdiendo la visibilidad del pipeline de ventas.  
**Qué falta:** Agregar `sync_lead_to_crm()` en `crm/service.py` y mapeador `lead_to_zoho_lead()` en `crm/mapper.py`. Invocar al crear/actualizar leads.

---

### 4.4 Sincronización CRM de Beneficiarios — Zoho Beneficiary ID Nunca Poblado (`app/modules/emission/models.py`)

**Severidad: MEDIA**

```python
zoho_beneficiary_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

Similar al caso anterior, el campo existe pero no hay código que lo llene. Los beneficiarios individuales con sus precios, `deceased_flag` y estados no se sincronizan a Zoho.

**Impacto:** Los "Beneficiary Snapshots" descritos en `INFRASTRUCTURE_OBSERVATIONS.md` como requisito crítico no se crean en el CRM.

---

### 4.5 Sincronización CRM de Suscripciones — Zoho Subscription ID Nunca Poblado (`app/modules/payments/models.py`)

**Severidad: MEDIA**

```python
zoho_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

El modelo `Subscription` tiene el campo `zoho_subscription_id` pero ningún código lo sincroniza con Zoho. Los campos de snapshot de suscripción (`mrr_snapshot`, `renewal_date`, `failed_payment_count`, `beneficiaries_count`) nunca se calculan ni envían al CRM.

---

### 4.6 Mapper de CRM Incompleto — Faltan Campos de Zoho (`app/modules/crm/mapper.py`)

**Severidad: MEDIA**

La función `client_to_zoho_contact()` mapea solamente 6 campos básicos:

```python
def client_to_zoho_contact(client) -> dict:
    return {
        "First_Name": client.first_name,
        "Last_Name": client.last_name,
        "Email": client.email,
        "Phone": client.phone,
        "Mailing_Country": client.country_of_residence,
        "Description": f"Doc: {client.document_type} {client.document_number}",
    }
```

El modelo `Client` tiene campos adicionales definidos que no se envían a Zoho: `churn_risk_level`, `collections_risk_level`, `chatwoot_contact_id`, `zoho_contact_id` (para actualización), `acquisition_channel`, `campaign_name`, `last_failed_payment_at`, etc.

De la misma forma, `policy_to_zoho_deal()` solo envía 5 campos básicos cuando Zoho requiere datos de beneficiarios, suscripción y atribución.

---

### 4.7 `get_or_create_customer()` Crea Clientes Duplicados en Stripe (`app/modules/payments/service.py`)

**Severidad: ALTA**

```python
# payments/service.py, líneas 26-31
async def get_or_create_customer(stripe: StripeClient, client_user: User) -> str:
    # In this MVP we check if metadata or a field has stripe_id
    # For now, we create a new one each time OR we assume one exists.
    customer = await stripe.create_customer(
        email=client_user.email,
        name=f"{client_user.first_name} {client_user.last_name}",
        metadata={"user_id": str(client_user.id)},
    )
    return customer["id"]
```

La función **siempre crea un nuevo cliente en Stripe** sin verificar si ya existe uno. El comentario reconoce el problema. Cada pago o creación de suscripción genera un customer duplicado en Stripe.

**Impacto:** Con el tiempo, Stripe acumula miles de clientes duplicados. Rompe la reconciliación financiera, impide el uso correcto de `stripe.Customer.list()` y puede generar errores al intentar crear suscripciones si hay constraints en Stripe.  
**Qué falta:** Guardar el `stripe_customer_id` en el modelo `Client` (campo a agregar) o buscar por email antes de crear.

---

### 4.8 Tarea de Checkouts Abandonados No Wired al Worker ARQ (`app/modules/leads/tasks.py`)

**Severidad: MEDIA**

La función `check_abandoned_checkouts()` está implementada en `app/modules/leads/tasks.py`:

```python
async def check_abandoned_checkouts() -> int:
    """
    Finds Policies in PENDING_PAYMENT status older than 24h
    and marks their linked Leads as abandoned.
    """
```

Sin embargo, la clase `WorkerSettings` en `app/workers/worker.py` **no incluye esta función** ni como tarea programada ni como función ad-hoc:

```python
class WorkerSettings:
    functions = [send_payment_reminders, retry_failed_payments]
    cron_jobs = [
        cron(send_payment_reminders, hour=9, minute=0),
        cron(retry_failed_payments, hour={6, 12, 18, 0}),
    ]
```

**Impacto:** Los leads abandonados nunca se marcan automáticamente como `abandoned_checkout_flag=True`. La lógica de recuperación de carritos (que depende de este flag para disparar secuencias en n8n) nunca se activa.

---

### 4.9 Dashboard — Acceso a Workspace Sin Protección (`app/modules/dashboard/router.py`)

**Severidad: MEDIA**

```python
# dashboard/router.py, línea 20
workspace_id = current_user.workspaces[0].id
```

Se accede al primer workspace del usuario directamente por índice `[0]` sin verificar si `workspaces` no está vacío. Cualquier usuario sin workspace asignado causará un `IndexError` al llamar al dashboard.

**Qué falta:** Agregar un guard: `if not current_user.workspaces: raise HTTPException(404, "No workspace found")`.

---

### 4.10 Templates de Email Ubicadas en Módulo Incorrecto

**Severidad: BAJA**

Los templates HTML de email (`email_policy_confirmation.html`, `email_payment_confirmed.html`, etc.) están en `app/modules/emission/templates/` junto con el `contract.html` del PDF, pero `EmailService` los busca en `app/modules/notifications/templates/`:

```python
# email_service.py, línea 31
templates_dir = Path(__file__).parent / "templates"
```

Como `email_service.py` está en `app/modules/notifications/`, la ruta apunta a `app/modules/notifications/templates/`. Sin embargo, este directorio **no existe** (`ls` confirma que no hay `templates/` en el módulo `notifications`).

**Impacto:** `EmailService` falla en runtime al intentar cargar cualquier template de email con `TemplateNotFound`. Todos los envíos de email fallan silenciosamente cuando `NOTIFICATIONS_ENABLED=True` o lanzan excepción.  
**Qué falta:** Crear el directorio `app/modules/notifications/templates/` y mover o symlink los templates de email desde `emission/templates/`.

---

### 4.11 Normalización E.164 de Teléfonos — Solo Almacenada, No Validada (`app/modules/leads/`)

**Severidad: MEDIA**

El documento `INFRASTRUCTURE_OBSERVATIONS.md` establece como regla crítica:

> *"El backend debe normalizar cada entrada y almacenar el original en `phone_raw` y el procesado en `phone_e164`."*

El modelo `Lead` tiene ambos campos (`phone_e164` y `phone_raw`), pero el schema `LeadCreate` define `phone_e164` como un `str` plano sin validación de formato E.164. No hay ningún validador Pydantic ni transformación que normalice el número antes de guardarlo. Se almacena lo que el cliente envíe.

**Impacto:** La "Regla de Oro" de deduplicación por `phone_e164` (usada en `create_or_update_lead()`) falla si dos requests envían el mismo número en formatos distintos (ej. `+13475551234` vs `13475551234`). Se crearán leads duplicados.

---

### 4.12 Migración de Alembic Faltante para Módulo AI y Leads

**Severidad: ALTA**

Las migraciones existentes son:
- `45de20cdff89_init.py`
- `a8657ef69ccf_auth_module.py`
- `003765469a84_plans_module.py`
- `046cf9ace8f0_emission_module.py`
- `32b4fc9d61a1_payments_module.py`
- `ecb513a9360b_add_vesting_periods_to_plan.py`

**No existe migración** para:
- Módulo `ai/` → tablas `knowledge_documents`, `chat_conversations`, `chat_messages`
- Módulo `leads/` → tabla `leads` (aunque se referencia con FK desde `policies.lead_id` en la migración `046cf9ace8f0_emission_module.py`)

La extensión `pgvector` tampoco está habilitada en ninguna migración, pero `KnowledgeDocument` usa `Vector(768)`.

**Impacto:** La base de datos no tiene estas tablas. El módulo AI falla en runtime al intentar insertar o consultar `knowledge_documents`. El endpoint `POST /emission/` podría fallar por FK inválida si `lead_id` se referencia a una tabla inexistente en producción.

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
