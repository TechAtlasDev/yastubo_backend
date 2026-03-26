# Hoja de Ruta de Refuerzo Arquitectónico - YASTUBO

Este documento detalla las acciones necesarias para transformar el backend actual en la "Máquina Autónoma" definitiva solicitada por YASTUBO.

## 1. Módulo IA (Orquestador LLM) [PRIORIDAD ALTA]
*   **Ubicación:** `app/modules/ai/`
*   **Objetivo:** Integrar OpenAI (GPT-4o/GPT-4-mini) para dinamizar las comunicaciones.
*   **Acciones:**
    *   Implementar un orquestador que reciba el contexto de la póliza y el evento (ej. pago fallido).
    *   Inyectar en `WhatsAppService` para enviar mensajes personalizados que reduzcan el churn.
    *   Preparar hooks para el futuro "Agente de Soporte de Voz (Dapta)".

## 2. Generación de Documentos Extendida
*   **Objetivo:** Cumplir con la entrega de "Passbook/Wallet" y "Vouchers".
*   **Acciones:**
    *   Investigar librerías para generación de archivos `.pkpass` (Apple Wallet).
    *   Crear plantilla HTML/CSS para el "Voucher de Asistencia" (tarjeta compacta).
    *   Automatizar el envío de estos documentos tras el `PAYMENT_SUCCEEDED`.

## 3. Venta Capitados (Carga Masiva Bulk)
*   **Objetivo:** Permitir a las agencias cargar beneficiarios por Excel.
*   **Acciones:**
    *   Implementar endpoint `POST /emission/bulk-upload`.
    *   Usar `pandas` para procesar el Excel y validar cada fila contra la lógica de `issue_policy`.
    *   Manejo de errores parciales (ej. "10 procesados, 2 fallaron por edad").

## 4. Dashboard de KPIs & Métricas (Máquina que Mide)
*   **Objetivo:** Visibilidad total para inversionistas/dueños.
*   **Acciones:**
    *   Crear vistas o queries optimizadas para calcular:
        *   **LTV (Lifetime Value):** Ingresos totales por cliente.
        *   **CAC (Customer Acquisition Cost):** Cruzar con datos de leads (CRM).
        *   **Churn Rate:** Porcentaje de pólizas canceladas vs activas mensualmente.

## 5. Refuerzo de Seguridad y CI/CD
*   **Acciones:**
    *   Asegurar que los Webhooks de Stripe tengan validación de firma (`signature verification`).
    *   Configurar entorno de Staging real para pruebas de integración con Zoho Sandbox.
