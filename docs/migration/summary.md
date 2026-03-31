# Resumen de Migración: Esquema Inventado a Real

Este documento resume el proceso de migración del backend de Yastubo hacia el esquema oficial extraído de `gfa-2025-02-26.sql`.

## 📌 Objetivos Alcanzados

Se ha completado la migración de la suite completa de módulos, asegurando que el sistema no solo refleje el esquema real, sino que sea funcional y escalable.

| Fase | Módulo | Cambios Clave |
| :--- | :--- | :--- |
| **T-01** | **Geography** | Implementación de `Country` (ISO2/ISO3) y `Zone`. |
| **T-02** | **Organizations** | Refactor de `Workspace` a jerarquía `Company` -> `BusinessUnit` con branding. |
| **T-03** | **Auth & Profiles** | Separación de `User` de `CustomerProfile`/`StaffProfile`. RBAC granular con scopes. |
| **T-04** | **Products** | Nueva jerarquía `Product` -> `Plan` -> `PlanVersion`. Precios por país y recargos por edad. |
| **T-05** | **Finance** | Manejo de `Currency`, `UnitOfMeasure` y lógica de dispersión de comisiones. |
| **T-06** | **Capitados** | Procesamiento masivo por batch (Excel) para seguros colectivos y conciliación. |

## 🛠️ Decisiones de Diseño

1.  **Versionado de Planes**: Se abandonó el uso de snapshots JSON en favor de una estructura normalizada (`PlanVersion`). Esto permite un control actuarial preciso y trazabilidad histórica.
2.  **Jerarquía de Organizaciones**: La migración de `Workspace` a `Company`/`BusinessUnit` permite soportar operaciones multi-oficina bajo una misma razón social.
3.  **Procesamiento de Capitados**: Se implementó un servicio batch con `openpyxl` que maneja errores a nivel de fila sin abortar el proceso completo, permitiendo la carga de miles de registros.
4.  **RBAC con Scopes**: Los permisos ahora están vinculados a ámbitos (`staff` vs `customer`), garantizando que los asegurados no accedan a funciones administrativas.

## 🧪 Validación y Calidad

- **Tests Totales**: **162** tests pasando (incluyendo el nuevo E2E).
- **Cobertura E2E**: Se añadió un test de integración (`tests/test_integration_e2e.py`) que valida el flujo completo: Creación de Empresa -> Producto -> Versión -> Carga Batch -> Cálculo de Precios.
- **Alembic**: La migración es lineal y puede ejecutarse desde una base de datos vacía (`alembic upgrade head`).

## 🚀 Próximos Pasos

1.  **Frontend**: Adaptar los componentes de UI para consumir los nuevos endpoints de versiones y capitados.
2.  **Reportes**: Implementar el módulo de reportería basado en las nuevas tablas de finanzas y records mensuales.
