---
title: Emission (Motor de Pólizas)
description: Gestión del ciclo de vida de seguros, clientes y generación de certificados.
---

El módulo de **Emission** es el corazón operativo de Yastubo. Se encarga de transformar una cotización en una póliza activa, gestionando los datos del asegurado y el estado legal del contrato a través de una máquina de estados determinista.

## Key Features

*   **State Machine Driven**: Cada póliza sigue un flujo de estados estricto (`DRAFT` -> `PENDING_PAYMENT` -> `ACTIVE` -> etc.).
*   **Gestión de Clientes**: Modelo de datos centralizado para beneficiarios y asegurados principales.
*   **Generación de Documentos**: Creación automática de certificados en PDF y Passbook de Apple/Google.
*   **Integración de Beneficiarios**: Gestión de hasta N beneficiarios por póliza con sus respectivos porcentajes.

:::caution[Validación Crítica]
El sistema impide cualquier transición de estado que no esté definida en la matriz de `VALID_TRANSITIONS`. Una póliza en mora (`IN_ARREARS`) solo puede volver a `ACTIVE` mediante la liquidación de la deuda pendiente.
:::

## Deep Dive Técnico

### La Máquina de Estados de la Póliza
El ciclo de vida de una póliza no es lineal y depende de eventos externos (pagos, reportes de siniestros). Los estados principales son:

*   **`DRAFT`**: La póliza está en borrador, esperando validación de datos.
*   **`PENDING_PAYMENT`**: Los datos son correctos, se espera la confirmación de la pasarela de pagos.
*   **`ACTIVE`**: El seguro está en vigor.
*   **`IN_ARREARS`**: Se ha detectado un impago en la suscripción recurrente.
*   **`CASE_REPORTED`**: Se ha abierto un siniestro asociado a la póliza.

### Lógica de Emisión
Cuando se emite una póliza, el sistema realiza las siguientes tareas en segundo plano:
1.  **Snapshot de Plan**: Vincula la póliza a la versión actual del plan para congelar las condiciones.
2.  **Generación de Certificado**: Crea un documento PDF con los datos del asegurado y las coberturas contratadas.
3.  **Sincronización de CRM**: Notifica al CRM (Zoho) sobre el nuevo cliente activo.

## Ejemplo Práctico: Cambio de Estado

El siguiente código muestra cómo se gestionan las transiciones de estado de forma segura:

```python
def transition(current: PolicyStatus, target: PolicyStatus) -> PolicyStatus:
    """
    Controlador de transiciones de estado para pólizas.
    Verifica que el salto de un estado a otro sea legal según la lógica de negocio.
    """
    VALID_TRANSITIONS = {
        PolicyStatus.DRAFT: [PolicyStatus.PENDING_PAYMENT, PolicyStatus.CANCELLED],
        PolicyStatus.PENDING_PAYMENT: [
            PolicyStatus.ACTIVE,
            PolicyStatus.CANCELLED,
            PolicyStatus.IN_ARREARS,
        ],
        PolicyStatus.ACTIVE: [
            PolicyStatus.IN_ARREARS,
            PolicyStatus.CANCELLED,
            PolicyStatus.CASE_REPORTED,
        ],
        # ... resto de transiciones
    }

    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Transición inválida: de {current} hacia {target}")
    
    return target
```

## Diagrama de Proceso

> [FLOW: Se crea una póliza en estado DRAFT. Al completar los datos, pasa a PENDING_PAYMENT. El webhook de Stripe confirma el pago. El sistema cambia el estado a ACTIVE e inicia la generación del PDF. La póliza se marca como emitida y se envía por email/WhatsApp al cliente].

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/emission/issue` | Creación inicial de una póliza (Draft). |
| `PATCH` | `/api/v1/emission/policies/{id}/status` | Cambio manual de estado (Solo ADMIN). |
| `GET` | `/api/v1/emission/policies/{id}/certificate` | Descarga del PDF oficial de la póliza. |
| `GET` | `/api/v1/emission/policies/me` | Lista de pólizas del usuario autenticado. |
