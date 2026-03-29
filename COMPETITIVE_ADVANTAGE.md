# Arsenal Competitivo - Yastubo Backend v1

Este documento es la **fuente única de verdad** para la estrategia, el negocio y la deuda técnica del proyecto.

---

## 🛡️ Nuestro Arsenal (Features Implementadas)

### 1. Experiencia de Desarrollador y Documentación
*   **Portal de Documentación con Starlight (Astro):** Sitio web técnico profesional en `/docs`.
*   **Terminal de Gestión (Interactive CLI):** TUI personalizada (`scripts/cli`) para administración rápida.
*   **Suite de Pruebas:** 80+ tests pasando (Stripe, Zoho, IA).

### 2. Inteligencia Artificial de Vanguardia
*   **IA con RAG (Retrieval-Augmented Generation):** Búsqueda semántica en documentos usando `pgvector`.
*   **Memoria Conversacional:** Historial persistente de 10 turnos en DB.
*   **Gemini 1.5 Flash:** Optimizado para respuestas rápidas y precisas.

### 3. Fintech y Pagos (Stripe Ecosystem)
*   **Stripe Connect (Multi-tenancy):** Gestión de Resellers con cobro de comisión automático.
*   **Gestión de Suscripciones:** Ciclo de vida completo y recurrente.
*   **Ajuste Dinámico por Fallecimiento:** Modificación automática de precios en Stripe ante siniestros.

### 4. Lógica de Negocio Avanzada
*   **Sistema de Auditoría (@audited):** Registro automático de acciones críticas.
*   **Máquina de Estados de Póliza:** Flujo riguroso de estados (DRAFT -> ACTIVE -> MORA).
*   **Sincronización Zoho CRM:** Integración asíncrona de Leads, Clientes y Pólizas.

---

## 🥷 Estrategia de "Robo Técnico" (Competencia)

### 1. De `santgm56` (Foco en Robustez)
*   **Repo:** [santgm56 - Reto-Yastubo-Masters-Backend](https://github.com/santgm56/Reto-Yastubo-Masters-Backend)
*   **Acción:** Implementar **Idempotencia de Eventos** (Tabla `StripeEvents`) y Guía de Demo Sandbox.

### 2. De `jsgalvish` (Foco en Estructura)
*   **Repo:** [jsgalvish - yastubo-python](https://github.com/jsgalvish/yastubo-python)
*   **Acción:** Implementar **Analítica de Negocio** (MRR, Churn Rate, Ratio de Siniestralidad).

### 3. Del Original `gfa-emisiones` (Foco en Negocio)
*   **Repo:** [Ariel Tapia - gfa-emisiones](https://github.com/arieltapiavillegas/gfa-emisiones)
*   **Acción:** **Módulo de Siniestros (Claims)** avanzado con rastreo de gastos y Reparto de Comisiones.

---

## ⚠️ Pendientes Críticos (Deuda Técnica de Producción)

Los siguientes ítems **rompen el sistema en producción (Runtime)** y deben resolverse con prioridad máxima:

1.  **StripeClient Incompleto (DT-03/04):** Faltan métodos `get_payment_method` y `get_customer_id_by_email`. El portal de usuario fallará.
2.  **Ruta de Templates de Email (DT-11):** `EmailService` no encuentra los archivos HTML. Las notificaciones fallarán.
3.  **Migraciones de DB (DT-10):** Faltan tablas para los módulos de `IA` y `Leads`. Requiere activar extensión `pgvector`.
4.  **Configuración de n8n (DT-05):** Falta `N8N_WEBHOOK_URL` en `Settings`. Toda la automatización externa está deshabilitada.

---

## 📜 Reglas de Oro de Negocio (Integridad)

Para asegurar la consistencia con el CRM y la operación de Yastubo:

*   **Clave Maestra:** El teléfono en formato **E.164** (`+1347...`) es el identificador único. No crear duplicados.
*   **Relación 1:N:** Una Póliza debe soportar múltiples Beneficiarios, cada uno con su propio `deceased_flag`.
*   **Atribución de Marketing:** Cada Lead debe capturar `utm_source`, `campaign_id` y canal de adquisición para medir el CAC real.

---

## 🚀 Roadmap de Expansión (The Gap Analysis)

1.  **Apple Wallet Real (DT-01):** Generar archivo `.pkpass` real (actualmente es un mock).
2.  **Voice AI Bridge (DT-02):** Implementar pipeline de voz con ElevenLabs y Twilio.
3.  **IA Claims Analyzer (DT-03):** Usar Gemini para analizar facturas y actas de defunción subidas por el usuario.
4.  **Checkout Abandonment:** Tarea programada para recuperar usuarios que no completaron el pago.
