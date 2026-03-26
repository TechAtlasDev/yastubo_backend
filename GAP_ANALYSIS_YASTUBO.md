# Análisis de Brechas Técnicas y Funcionales (Gap Analysis) - Proyecto YASTUBO

Este documento identifica las funcionalidades críticas que faltan en la implementación actual para cumplir con los requerimientos del reto YASTUBO y asegurar una ventaja competitiva en la evaluación.

## 1. Capa de Inteligencia Artificial (IA-First) [URGENTE]
El sistema actual es reactivo. Para ser una "Máquina Autónoma", requiere:
*   **Orquestador LLM (WhatsApp/Email):** Implementar `app/modules/ai/` para integrar OpenAI/Anthropic. Los mensajes no deben ser plantillas estáticas, sino respuestas dinámicas que resuelvan dudas y guíen al usuario.
*   **Agente de Soporte de Voz:** Integración con Dapta/ElevenLabs para automatización de llamadas de asistencia y cobro.
*   **Clasificación Automática de Leads:** El LLM debe analizar las conversaciones de WhatsApp para marcar leads como "Hot", "Warm" o "Cold" en el CRM Zoho.

## 2. Documentación Digital Moderna [IMPACTO VISUAL]
El contrato PDF es funcional, pero faltan los entregables móviles:
*   **Apple Wallet / Google Pay (.pkpass):** Generación automática de pases de suscripción.
*   **Voucher de Asistencia:** Una tarjeta visual compacta con los números de emergencia y datos clave, disparada tras el `PAYMENT_SUCCEEDED`.

## 3. Funcionalidades de Negocio "Stretch" (Diferenciadores)
*   **Venta Capitados (Bulk Upload):** Implementar la carga masiva de beneficiarios vía Excel (Pandas) con validaciones de motor de reglas.
*   **Funnel de Venta Directa (Self-Serve):** Landing page/API pública para suscripción en <3 minutos sin intervención de un vendedor.
*   **Lógica de Dunning (Reintentos de Cobro):** Automatizar 2-3 intentos de cobro en Stripe antes de marcar la póliza como "MORA" o "CANCELADA".
*   **Atribución de Marketing:** Hooks para Meta Pixel y Google Ads API para medir el CAC real por canal e influencer.

## 4. Gestión de Canales y Comisiones
*   **Stripe Connect (Pay-outs):** Implementar la dispersión automática de comisiones a los vendedores freelance una vez que el pago del cliente sea exitoso.
*   **Portal de Agencias:** Refinar los filtros de visibilidad para que las agencias solo vean sus propios datos y métricas.

## 5. La Máquina que Mide (Dashboard de KPIs)
El backend debe exponer endpoints para calcular:
*   **LTV (Lifetime Value):** Valor de vida del cliente.
*   **CAC (Customer Acquisition Cost):** Costo de adquisición.
*   **Churn Rate:** Tasa de cancelación mensual.
*   **Análisis de Cohortes:** Comportamiento de usuarios por mes de entrada.

## 6. Automatizaciones de Marketing (Retargeting)
*   **Trigger de Abandono:** Si un usuario inicia el registro pero no paga, disparar un webhook hacia n8n/Zapier para iniciar una secuencia de recuperación en WhatsApp/Email.

---
**Nota para el Arquitecto:** La base técnica es de 10/10. El éxito depende ahora de la ejecución de esta "Capa de Inteligencia" y la "Automatización Total".
