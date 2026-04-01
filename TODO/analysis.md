# 🔍 Análisis Exhaustivo de Brechas (Gap Analysis) - Yastubo Backend v1 🚀

Este documento detalla las discrepancias entre la infraestructura actual de Yastubo y los requisitos reales extraídos del volcado oficial de base de datos (`gfa-2025-02-26.sql`).

---

## 1. 📂 Módulos Críticos Faltantes (Arquitectura de Producto)

### 🧩 Módulo de "Capitados" (Seguros Colectivos)
Nuestra mayor brecha. El sistema actual solo maneja ingresos individuales, pero la DB oficial está diseñada para la gestión masiva de colectivos.
- **Entidades Faltantes**: `capitados_contracts`, `capitados_monthly_records`, `capitados_batch_logs`.
- **Funcionalidad Necesaria**: Procesamiento de archivos Excel (Batch de 2000+ filas), lógica de "mismo asegurado en distintos productos", y estados de conciliación mensual.

### 🏢 Módulo de "Business Units" (Organización Jerárquica)
Actualmente usamos `Workspaces` planos. La realidad exige una jerarquía corporativa.
- **Garantía de Escala**: Una empresa (`Company`) puede tener múltiples oficinas (`Offices`) o agencias bajo su mando.
- **Branding**: Cada unidad debe poder sobreescribir colores y logos (`branding_logo_file_id`, `branding_bg_dark`, etc.).

---

## 2. 🖋️ Rediseño de "Plans" a "Product System"

Nuestra implementación de `plans` es demasiado simplista. La DB oficial propone:
1.  **Product Hierarchy**: Un Producto (`Product`) es el padre. Este contiene múltiples versiones (`PlanVersion`).
2.  **Versionado Real**: No basta con un JSON `snapshot`. Cada versión debe tener sus propias relaciones a:
    - `plan_version_age_surcharges`: Recargos por edad detallados.
    - `plan_version_countries`: Precios específicos por país de residencia.
    - `plan_version_coverages`: Valores de cobertura (decimales, enteros o texto) por versión.
    - `plan_version_repatriation_countries`: Listado formal de países permitidos.
3.  **Tiempos de Carencia (Vesting)**: Deben integrarse formalmente (`wtime_suicide`, `wtime_accident`, `wtime_preexisting`).

---

## 3. 💳 Finanzas y Comisiones

El sistema actual carece de lógica de dispersión de fondos:
- **Comisiones Dinámicas**: Tablas como `company_commission_users` sugieren que por cada venta, el sistema debe repartir porcentajes entre la compañía, la unidad de negocio y el agente.
- **Monedas y Unidades**: Debemos integrar un manejo centralizado de `currencies` y `units_of_measure`.

---

## 4. 🔐 Seguridad y Auditoría Avanzada

- **RBAC Granular**: Necesitamos migrar de roles simples a un sistema de permisos basado en niveles y ámbitos (`guard_name`, `scope`).
- **Perfiles de Usuario**: Separar la entidad `User` de sus perfiles específicos (`customer_profiles` para asegurados, `staff_profiles` para agentes/admin).
- **Password History**: Implementar cumplimiento de seguridad para no repetir contraseñas anteriores.

---

## 5. 🗺️ Geografía Centralizada

Nuestros países son hoy simples strings o configuraciones dentro del plan.
- **Requirement**: Un módulo global de `geografía` que maneje `countries` (ISO2/ISO3, phone_codes) y `zones` (agrupaciones de países por riesgo).

---

## 📋 Lista de Tareas Inmediatas (Roadmap de Corrección)

1.  **[ ] Refactor de `app/modules/workspaces`**: Convertir en `app/modules/organizations` con soporte de jerarquía.
2.  **[ ] Refactor de `app/modules/plans`**: Implementar la tríada `Product` -> `Plan` -> `Version`.
3.  **[ ] Crear `app/modules/capitados`**: Empezar por los modelos de contratos colectivos y la lógica de carga mensual.
4.  **[ ] Evolucionar `app/modules/auth`**: Añadir perfiles (`customer_profiles`) y el sistema de comisiones base.
5.  **[ ] Integración de Plantillas**: Crear módulo `templates` para manejar contratos legales y documentos por versión de plan.

---
**Nota**: Este análisis es vital para el concurso, ya que demuestra que el sistema puede escalar a operaciones reales de miles de asegurados bajo estructuras corporativas complejas.
