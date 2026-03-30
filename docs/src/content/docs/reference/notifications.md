---
title: Notifications (Alertas y Canales)
description: Sistema de comunicación omnicanal a través de Email y WhatsApp.
---

El módulo de **Notifications** gestiona la comunicación directa con el asegurado y los vendedores. Se encarga de enviar certificados, recordatorios de pago y alertas de seguridad a través de múltiples canales integrados.

## Key Features

*   **Email Engine**: Envío masivo de pólizas en PDF y comunicaciones transaccionales (AWS SES o SendGrid).
*   **WhatsApp API Integration**: Notificaciones interactivas para confirmación de pago y recordatorios de mora.
*   **Gestión de Plantillas**: Sistema centralizado de templates para mantener la consistencia de marca.
*   **Retry Policy**: Lógica de reintento integrada para asegurar la entrega de mensajes críticos.

:::tip[Estrategia Multicanal]
El sistema envía la póliza por email inmediatamente al emitirse, pero utiliza WhatsApp para recordatorios de pago de segundo nivel si detecta que una suscripción ha fallado dos veces seguidas.
:::

## Deep Dive Técnico

### Integración de Canales
El servicio de notificaciones actúa como una fachada (`Facade`) que orquesta múltiples proveedores:

1.  **EmailService**: 
    *   Adjunta dinámicamente el certificado PDF generado por el módulo de Emission.
    *   Utiliza plantillas HTML responsivas.
2.  **WhatsAppService**:
    *   Envía mensajes de texto y documentos a través de proveedores externos.
    *   Enfocado en mensajes de alta urgencia (Mora, Emisión Exitosa).

### Orquestación de Eventos
Las notificaciones no se invocan de forma aislada, sino que responden a eventos de negocio:
*   **`on_policy_issued`**: Dispara el envío del PDF por ambos canales.
*   **`on_payment_failed`**: Lógica condicional: Email en el primer fallo, WhatsApp se añade en el segundo.

## Ejemplo Práctico: Orquestador de Alertas

El siguiente código muestra cómo se distribuyen las notificaciones según el evento de negocio:

```python
class NotificationsService:
    """
    Servicio unificado para la gestión de notificaciones omnicanal.
    """
    async def on_policy_issued(self, policy, client, pdf_bytes: bytes) -> None:
        """
        Notificación inmediata de nueva póliza emitida.
        Envía Email con PDF adjunto y mensaje de bienvenida por WhatsApp.
        """
        # Envío asíncrono por Email
        await self.email.send_policy_confirmation(policy, client, pdf_bytes)
        
        # Envío asíncrono por WhatsApp
        await self.whatsapp.send_policy_confirmation_wa(policy, client)

    async def on_payment_failed(self, policy, client, attempt: int) -> None:
        """
        Lógica de escalonamiento de recordatorios de pago.
        """
        # Siempre se envía un Email de aviso de fallo
        await self.email.send_payment_failed(policy, client, attempt)
        
        # WhatsApp solo se activa a partir del segundo intento fallido (urgencia alta)
        if attempt >= 2:
            await self.whatsapp.send_payment_reminder_wa(policy, client)
```

## Diagrama de Proceso

![Notifications Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774845094/123fc06c-007b-4ef7-a418-3b14b5838730.png)

## Canales Disponibles

| Canal | Propósito | Formato |
| :--- | :--- | :--- |
| **Email** | Comunicación formal, envío de adjuntos, soporte. | HTML / PDF |
| **WhatsApp** | Recordatorios rápidos, confirmación instantánea. | Texto / Documentos |
| **Push (Planes)** | Notificaciones en app móvil (en roadmap). | Texto / Acción |
