# Inventario de Endpoints — Demo Yastubo

Este documento detalla los endpoints reales encontrados en el backend para el mapeo del dashboard de la demo.

## Módulo: Auth (Authentication)
*   **POST /api/v1/auth/register**
    *   **Descripción:** Registra un nuevo usuario (rol CLIENTE por defecto).
    *   **Payload:** `UserRegister` (email, full_name, phone, password).
    *   **Retorno:** `UserResponse` con roles.
*   **POST /api/v1/auth/login**
    *   **Descripción:** Autentica usuario y genera tokens JWT.
    *   **Payload:** `UserLogin` (email, password).
    *   **Retorno:** `TokenResponse` (access_token, refresh_token).
*   **GET /api/v1/auth/me**
    *   **Descripción:** Obtiene el perfil del usuario actual.
    *   **Retorno:** `UserResponse` con empresas asociadas.
*   **POST /api/v1/auth/roles/assign**
    *   **Descripción:** Asigna roles a un usuario (requiere ADMIN).
    *   **Payload:** `RoleAssign` (user_id, role_name).

## Módulo: Plans (Products & Pricing)
*   **GET /api/v1/products/**
    *   **Descripción:** Lista productos activos con sus planes y versiones.
    *   **Retorno:** `List[ProductResponse]`.
*   **POST /api/v1/products/**
    *   **Descripción:** Crea un producto complejo (árbol: Producto -> Plan -> Versión -> Recargos/Países/Coberturas).
    *   **Payload:** `ProductCreate` (name, description, product_type, plans: []).
    *   **Auth:** ADMIN.
*   **POST /api/v1/plans/calculate-price**
    *   **Descripción:** Calcula el precio final basado en edad, país y cantidad.
    *   **Payload:** `PriceCalculationRequest` (plan_version_id, country_code, age, quantity).

## Módulo: Emission (Individual & Bulk)
*   **POST /api/v1/emission/clients**
    *   **Descripción:** Registra un cliente (tomador de póliza).
    *   **Payload:** `ClientCreate`.
*   **POST /api/v1/emission/issue**
    *   **Descripción:** Emite una póliza individual.
    *   **Payload:** `EmissionRequest` (client_id, plan_version_id, beneficiaries: []).
*   **GET /api/v1/emission/policies**
    *   **Descripción:** Lista pólizas emitidas.
*   **POST /api/v1/emission/bulk-upload**
    *   **Descripción:** Emisión masiva vía Excel (alternativa a módulo capitados).

## Módulo: Capitados (Batch Processing)
*   **POST /api/v1/capitados/batches/upload**
    *   **Descripción:** Sube Excel de capitados para procesamiento en background.
    *   **Payload:** `multipart/form-data` (company_id, coverage_month, file).
*   **GET /api/v1/capitados/batches/{batch_id}**
    *   **Descripción:** Estado del lote (pending, processing, completed, error) y resumen de filas.
*   **GET /api/v1/capitados/batches/{batch_id}/items**
    *   **Descripción:** Detalle fila por fila del procesamiento (logs de éxito/error).

## Módulo: Finance (Commissions)
*   **POST /api/v1/finance/commissions/calculate**
    *   **Descripción:** Calcula la dispersión de comisiones para un monto.
    *   **Payload:** `CommissionDispersionRequest` (amount, company_id, business_unit_id).
*   **GET /api/v1/finance/currencies**
    *   **Descripción:** Lista monedas activas.

## Módulo: Dashboard (Analytics)
*   **GET /api/v1/dashboard/metrics**
    *   **Descripción:** KPIs globales: Total pólizas, primas, siniestros y comisiones.
    *   **Auth:** ADMIN.

## Módulo: Audit (Tracking)
*   **GET /api/v1/audit/**
    *   **Descripción:** Logs de actividad del sistema (quién hizo qué y cuándo).
    *   **Auth:** ADMIN.

## Módulo: AI & Voice
*   **POST /api/v1/ai/chat**
    *   **Descripción:** Chat con contexto de base de conocimiento.
*   **POST /api/v1/voice/incoming-call**
    *   **Descripción:** Endpoint TwiML para asistente de voz.
