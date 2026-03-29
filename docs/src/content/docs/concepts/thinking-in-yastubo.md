---
title: Thinking in Yastubo
description: La filosofía y estrategia detrás de la protección para migrantes.
---

Yastubo no es simplemente un software de gestión de seguros; es un ecosistema diseñado para resolver la fricción inherente a la movilidad humana internacional. Nuestra arquitectura refleja el compromiso de proteger a quienes se encuentran lejos de su hogar, priorizando la **dignidad**, la **velocidad** y la **precisión operativa**.

## Core Benefits

*   **Identidad Centrada en la Movilidad:** Utilizamos el número de teléfono en formato **E.164** como ancla de identidad, reconociendo que para un migrante, su número de contacto es más persistente que su dirección física.
*   **Resiliencia Actuarial:** El sistema ajusta dinámicamente el riesgo basándose en la ubicación y edad de los beneficiarios, permitiendo una cobertura justa en tiempo real.
*   **Transparencia Total:** Cada interacción, desde el primer contacto del lead hasta el cierre de un siniestro, es auditable y trazable.

## Deep Dive Técnico: El Modelo de Datos Humano

A diferencia de los sistemas tradicionales donde una póliza es una entidad estática, en Yastubo la póliza es un **ente vivo**. 

### Relación 1:N y el Deceased Flag
El backend permite que una única suscripción cubra a múltiples beneficiarios. Técnicamente, esto se gestiona mediante una relación uno a muchos donde cada beneficiario posee un flag `deceased_flag`. 

:::tip[Impacto en el Negocio]
Cuando un beneficiario es marcado como fallecido tras la validación de un siniestro, el sistema recalcula automáticamente la suscripción en Stripe, reduciendo el costo para el cliente de forma inmediata sin intervención manual.
:::

### Atribución y Adquisición
Entendemos que el costo de adquisición (CAC) es crítico. Por ello, cada lead captura metadatos de marketing (`utm_source`, `campaign_id`) que se propagan a lo largo de todo el ciclo de vida, permitiendo al equipo de operaciones optimizar la inversión en los canales que realmente protegen a más familias.

## Ejemplo: Identificación Única

```python
# app/modules/leads/schemas.py
from pydantic import BaseModel, Field

class LeadCreate(BaseModel):
    # El teléfono es nuestra clave maestra de identidad
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", example="+13471234567")
    full_name: str
    email: str
    country_code: str # País de origen/destino
```
*El formato E.164 asegura la compatibilidad global para notificaciones de WhatsApp y sincronización con el CRM.*

## Diagrama de Filosofía de Servicio

> [FLOW: El proceso inicia en el "Lead" capturado con metadatos UTM, fluye hacia la "Emisión" de la póliza vinculando múltiples "Beneficiarios". Si ocurre un "Siniestro", la transición de estado dispara tanto el "Servicio de Asistencia" como el "Ajuste de Precio en Stripe", cerrando el ciclo con la actualización en "Zoho CRM"].
