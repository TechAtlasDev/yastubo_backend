# 📊 MIGRATION_BASELINE.md - Yastubo Backend v1 🚀

Este documento establece el punto de partida (Baseline) para la migración del esquema de base de datos desde el sistema inventado actual al esquema real extraído de `gfa_official_backup.sql`.

---

## 🏗️ 1. Estado de la Base de Datos Actual (PostgreSQL/SQLAlchemy)

El sistema usa SQLAlchemy con PostgreSQL en producción/desarrollo y SQLite en memoria para tests.

### 📋 Inventario de Tablas Actuales (SQLAlchemy)
Se han identificado 27 tablas en los modelos actuales del proyecto:

| Módulo | Tablas identificadas |
| :--- | :--- |
| **Auth** | `users`, `roles`, `permissions`, `user_roles`, `role_permissions` |
| **Workspaces** | `workspaces`, `user_workspaces` |
| **Plans** | `plans`, `plan_versions`, `coverages`, `plan_coverages`, `age_ranges`, `country_configs` |
| **Emission** | `clients`, `policies`, `beneficiaries`, `policy_status_history` |
| **Leads** | `leads`, `lead_history` (en service), `lead_ai_analysis` |
| **Payments** | `transactions`, `stripe_events` |
| **Claims** | `claims`, `claim_expenses`, `commission_distributions` |
| **AI** | `chat_conversations`, `chat_messages`, `knowledge_documents` |
| **Audit** | `audit_logs` |

### 🛠️ Versión de Alembic (Actualizada)
- **Current Head**: `cfcc3aa64589` (baseline_and_geography)
- **Estado**: ✅ **Consistente**. Se eliminaron las migraciones vacías y se generó una nueva migración base.
- **Cambios Infraestructura**: El contenedor PostgreSQL se actualizó a la imagen `pgvector/pgvector:pg16` para soportar extensiones de vectores.

---

## 🏛️ 2. Estado de la Base de Datos Real (Legacy MySQL)

El esquema real extraído del backup MySQL (`gfa_official_backup.sql`) cuenta con **50 tablas**.

### 📋 Inventario de Tablas Reales (MySQL)
| Categoría | Tablas Principales |
| :--- | :--- |
| **Org / Unidades** | `companies`, `business_units`, `memberships_business_unit`, `company_user` |
| **Productos / Planes** | `products`, `plan_versions`, `plan_version_age_surcharges`, `plan_version_countries`, `plan_version_coverages`, `plan_version_repatriation_countries` |
| **Capitados (Grupales)** | `capitados_contracts`, `capitados_monthly_records`, `capitados_product_insureds`, `capitados_batch_logs` |
| **Perfiles / Seguridad** | `customer_profiles`, `staff_profiles`, `password_histories`, `roles`, `permissions` (RBAC granular) |
| **Finanzas** | `business_unit_commission_users`, `company_commission_users` |
| **Geografía / Config** | `countries`, `zones`, `country_zone`, `units_of_measure`, `templates` |

---

## 🧪 3. Verificación de Tests (Baseline)

Se ejecutó la suite completa de tests para validar el estado funcional antes de cualquier cambio.

- **Total de Tests**: 147
- **Resultado**: ✅ **147 PASSED**
- **Configuración**: Los tests corren sobre **SQLite in-memory**, lo que les permite ser independientes de las inconsistencias de las migraciones Alembic por ahora.

---

## 🚩 4. Resumen de Brechas Críticas

1.  **Estructura de Planes**: El sistema actual usa un `JSON snapshot` para versiones, mientras que el esquema real usa relaciones normalizadas.
2.  **Organización**: Falta la jerarquía `Company` -> `BusinessUnit`.
3.  **Capitados**: No existe soporte para seguros colectivos masivos en el sistema actual.
4.  **Perfiles**: La separación entre `User` y sus perfiles (`customer`/`staff`) es inexistente en SQLAlchemy.

---
## 🏁 5. Registro de Tareas de Migración

| ID | Tarea | Estado | Observaciones |
| :--- | :--- | :--- | :--- |
| **T-01** | **Módulo de Geografía** | ✅ COMPLETADA | Modelos `Country` y `Zone` creados. Router, Service y Tests funcionando. |
| **T-02** | **Org Hierarchical** | ✅ COMPLETADA | Migración de `Workspace` a jerarquía `Company -> BusinessUnit` finalizada. |
| **T-03** | **Plan Normalization**| ✅ COMPLETADA | Estructura `Product -> Plan -> PlanVersion` con tablas relacionales implementada. |
| **T-04** | **Capitados System**  | ✅ COMPLETADA | Soporte para seguros colectivos, batches y registros mensuales. |
| **T-05** | **Auth & RBAC Refactor**| ✅ COMPLETADA | Perfiles de staff/cliente y permisos granulares integrados. |
| **T-06** | **Final Integration** | ✅ COMPLETADA | Verificación de estado limpio y documentación técnica actualizada. |

---
**Nota**: El sistema ha superado la fase de baseline y se encuentra en un estado de **Feature Ready** para los módulos core de la migración.
