# 🗺️ ROADMAP DE MIGRACIÓN — Yastubo Backend v2

**Propósito:** Plan de ejecución ordenado para migrar el backend de Yastubo desde el esquema inventado al esquema real (`gfa-2025-02-26.sql`), adaptando modelos, servicios, tests y documentación.

**Cómo usar este documento:**
Cada tarea tiene un bloque `## PROMPT DE TAREA` listo para copiar y pegar al asistente. Las tareas están ordenadas por dependencia — no asignes una tarea si sus prerequisitos no están completos.

**Estado de cada tarea:** `[ ]` pendiente · `[~]` en progreso · `[x]` completa

---

## 📊 Resumen de Fases

| Fase | Nombre | Tareas | Dependencias |
|------|--------|--------|--------------|
| 0 | Base y análisis | T-00 | — |
| 1 | Geografía y catálogos | T-01 | T-00 |
| 2 | Organizaciones | T-02 | T-01 |
| 3 | Autenticación y perfiles | T-03 | T-02 |
| 4 | Sistema de productos | T-04 | T-03 |
| 5 | Finanzas y comisiones | T-05 | T-04 |
| 6 | Capitados | T-06 | T-04, T-05 |
| 7 | Integración y cierre | T-07 | T-01…T-06 |

---

## FASE 0 — Base y Análisis

### [ ] T-00 · Análisis de brechas y configuración del entorno

**Objetivo:** Confirmar que el análisis de brechas es correcto, validar que el entorno corre con el esquema actual y establecer la línea base antes de cualquier cambio.

**Prerequisitos:** Ninguno.

**Entregables esperados:**
- Confirmación de que el entorno levanta (`docker compose up` o equivalente)
- Suite de tests existente en verde
- Archivo `MIGRATION_BASELINE.md` en la raíz con el estado inicial documentado: versión de Alembic actual, tablas existentes, endpoints funcionales

**Criterio de éxito:** El asistente puede correr los tests y confirmar cuántos pasan antes de tocar nada.

---

## FASE 1 — Geografía y Catálogos

### [ ] T-01 · Módulo de geografía (`countries` y `zones`)

**Objetivo:** Crear el módulo base de geografía que otros módulos usarán como referencia. Debe estar primero porque `organizations`, `plans` y `capitados` dependen de él.

**Prerequisitos:** T-00 completo.

**Alcance:**
- Modelos SQLAlchemy: `Country`, `Zone`
- Campos: código ISO2, ISO3, nombre, código telefónico, zona de riesgo asociada
- Migración Alembic con `upgrade()` y `downgrade()`
- Seed inicial con los países relevantes para la operación (mínimo los del esquema real)
- Repositorio y servicio básico (CRUD de consulta, sin lógica compleja)
- Endpoint de listado (`GET /geography/countries`, `GET /geography/zones`)
- Tests unitarios del servicio y de integración del endpoint
- Página de documentación en `docs/` bajo `docs/modules/geography.md`

**Criterio de éxito:** `GET /geography/countries` retorna la lista correcta; migración corre en ambas direcciones sin error.

---

## FASE 2 — Organizaciones

### [x] T-02 · Refactor de `workspaces` a `organizations` (jerarquía corporativa)

**Objetivo:** Reemplazar el modelo plano de `Workspace` por la jerarquía real: `Company` → `Office/Agency`. Incluir soporte de branding por unidad.

**Prerequisitos:** T-01 completo.

**Alcance:**
- Deprecar modelo `Workspace` (migración que renombra/transforma la tabla existente)
- Nuevos modelos: `Company`, `BusinessUnit` (oficinas o agencias bajo una empresa)
- Campos de branding: `branding_logo_file_id`, `branding_bg_dark`, `branding_bg_light`, y los que estén en el esquema real
- Actualizar todas las foreign keys que apuntaban a `workspaces`
- Adaptar servicios y repositorios afectados
- Actualizar endpoints existentes o crear los nuevos necesarios
- Tests: unitarios de servicio, integración de endpoints, test de migración (upgrade + downgrade)
- Documentación: `docs/modules/organizations.md`

**Criterio de éxito:** La jerarquía Company → BusinessUnit funciona; los endpoints anteriores de workspaces siguen respondiendo (con redirección o adaptación) o están documentados como breaking change.

---

```
## PROMPT DE TAREA — T-02

Tarea: Refactor de workspaces → organizations con jerarquía corporativa

Prerequisitos completados: T-00, T-01.

Lee el esquema real en TODO/ para identificar las tablas de organizaciones (companies, business_units, offices o equivalentes). Lee la documentación actual del módulo workspaces en docs/.

Ejecuta en orden:
1. Diseña el plan de migración: qué datos de workspaces se preservan, qué se transforma, qué se descarta. Documenta las decisiones antes de ejecutar.
2. Crea los nuevos modelos SQLAlchemy: Company, BusinessUnit con sus campos de branding.
3. Genera la migración Alembic que transforma workspaces al nuevo esquema. Implementa downgrade().
4. Actualiza todas las referencias a workspace_id en el resto del código.
5. Adapta servicios, repositorios y endpoints.
6. Corre todos los tests. Corrige los que fallen por el cambio de esquema.
7. Escribe tests nuevos para la jerarquía Company → BusinessUnit.
8. Crea docs/modules/organizations.md.
9. Haz commit.

Si hay breaking changes en la API, documéntalos explícitamente antes de hacer commit.
```

---

## FASE 3 — Autenticación y Perfiles

### [x] T-03 · Evolución del módulo `auth` — perfiles y seguridad avanzada

**Objetivo:** Separar la entidad `User` de sus perfiles de rol (`customer_profiles` para asegurados, `staff_profiles` para agentes/admin), implementar RBAC granular y control de historial de contraseñas.

**Prerequisitos:** T-02 completo.

**Alcance:**
- Nuevos modelos: `CustomerProfile`, `StaffProfile`
- Sistema de permisos: roles con `guard_name` y `scope` según el esquema real
- `PasswordHistory`: tabla para control de reutilización
- Migración que preserva los usuarios existentes asignándoles perfil correcto
- Actualizar middleware/dependencias de autenticación que usen el modelo `User`
- Tests de seguridad: acceso denegado por scope, reutilización de contraseña rechazada
- Documentación: `docs/modules/auth.md` actualizado

**Criterio de éxito:** Un usuario con rol `staff` no puede acceder a endpoints de `customer`; el sistema rechaza contraseñas repetidas.

---

```
## PROMPT DE TAREA — T-03

Tarea: Evolución del módulo auth — perfiles de usuario y RBAC granular

Prerequisitos completados: T-00, T-01, T-02.

Lee el esquema real en TODO/ para identificar: customer_profiles, staff_profiles, la estructura de roles/permisos y password_history. Lee docs/modules/auth.md (documentación actual).

Ejecuta en orden:
1. Crea los modelos CustomerProfile y StaffProfile con sus campos según el esquema real.
2. Implementa la tabla de roles/permisos con guard_name y scope.
3. Implementa PasswordHistory.
4. Genera las migraciones Alembic. Incluye lógica de migración de datos: asigna perfil a usuarios existentes según su rol actual.
5. Actualiza el middleware de autenticación y las dependencias FastAPI que usen User directamente.
6. Escribe tests: separación de perfiles, RBAC por scope, rechazo de contraseña repetida.
7. Corre toda la suite. Corrige regresiones.
8. Actualiza docs/modules/auth.md.
9. Haz commit.
```

---

## FASE 4 — Sistema de Productos

### [x] T-04 · Refactor de `plans` al sistema Product → Plan → PlanVersion

**Objetivo:** Reemplazar el modelo plano de `plans` por la jerarquía real de tres niveles con soporte de recargos por edad, precios por país, coberturas versionadas y tiempos de carencia.

**Prerequisitos:** T-01 (geografía), T-03 (auth) completos.

**Alcance:**
- Nuevos modelos:
  - `Product` — entidad padre
  - `Plan` — versión comercial del producto
  - `PlanVersion` — versión técnica con sus propias relaciones
  - `PlanVersionAgeSurcharge` — recargos por rango de edad
  - `PlanVersionCountry` — precios por país de residencia
  - `PlanVersionCoverage` — valores de cobertura (decimal, entero o texto)
  - `PlanVersionRepatriationCountry` — países permitidos para repatriación
- Campos de carencia: `wtime_suicide`, `wtime_accident`, `wtime_preexisting`
- Migración que transforma los `plans` existentes al nuevo esquema (con snapshot JSON como fallback si aplica)
- Adaptar servicios que usen el modelo `Plan` antiguo
- Tests: creación de producto con versiones, precios por país, validación de carencias
- Documentación: `docs/modules/products.md`

**Criterio de éxito:** Se puede crear un producto con dos versiones de plan, cada una con precios distintos por país y coberturas distintas.

---

```
## PROMPT DE TAREA — T-04

Tarea: Refactor de plans → sistema Product → Plan → PlanVersion

Prerequisitos completados: T-00, T-01, T-02, T-03.

Lee el esquema real en TODO/ para identificar toda la jerarquía de productos y versiones. Lee la documentación actual del módulo plans en docs/.

Ejecuta en orden:
1. Diseña el nuevo esquema de modelos completo antes de escribir código. Muéstramelo para validación.
2. Crea los modelos: Product, Plan, PlanVersion y todas las tablas de detalle (surcharges, countries, coverages, repatriation_countries).
3. Genera las migraciones Alembic. La migración de datos debe transformar los planes existentes al nuevo esquema sin pérdida de información.
4. Adapta todos los servicios, repositorios y endpoints que usen el modelo Plan antiguo.
5. Escribe tests: ciclo completo de creación de producto con versiones, precios por país, coberturas, validación de tiempos de carencia.
6. Corre toda la suite. Corrige regresiones.
7. Crea docs/modules/products.md con diagrama ER en Mermaid.
8. Haz commit.

IMPORTANTE: En el paso 1, espera mi confirmación del diseño antes de continuar.
```

---

## FASE 5 — Finanzas y Comisiones

### [ ] T-05 · Módulo de finanzas — currencies, units y comisiones dinámicas

**Objetivo:** Implementar el manejo centralizado de monedas y unidades de medida, y la lógica de dispersión de comisiones entre compañía, unidad de negocio y agente.

**Prerequisitos:** T-02 (organizations), T-04 (products) completos.

**Alcance:**
- Nuevos modelos: `Currency`, `UnitOfMeasure`
- Modelo `CompanyCommissionUser`: porcentajes de comisión por venta para cada actor
- Servicio de cálculo y dispersión de comisiones
- Integración con el flujo de venta existente (si existe) o stub documentado
- Tests: cálculo correcto de dispersión con tres actores, casos borde (porcentajes que no suman 100%, actores faltantes)
- Documentación: `docs/modules/finance.md`

**Criterio de éxito:** Dado una venta, el sistema calcula correctamente cuánto corresponde a cada actor según la configuración de comisiones.

---

```
## PROMPT DE TAREA — T-05

Tarea: Módulo de finanzas — currencies, units y comisiones dinámicas

Prerequisitos completados: T-00 al T-04.

Lee el esquema real en TODO/ para identificar: currencies, units_of_measure, company_commission_users y tablas relacionadas. Lee docs/ para entender cómo se maneja actualmente el flujo de venta.

Ejecuta en orden:
1. Crea los modelos Currency y UnitOfMeasure con seed de datos iniciales.
2. Crea el modelo CompanyCommissionUser con su lógica de porcentajes.
3. Implementa el servicio de cálculo de dispersión de comisiones.
4. Integra con el flujo de venta existente. Si no hay flujo de venta aún, crea un stub documentado.
5. Genera migraciones Alembic.
6. Escribe tests: caso feliz de dispersión, porcentajes que no suman 100% (debe lanzar error), actor faltante.
7. Corre toda la suite.
8. Crea docs/modules/finance.md.
9. Haz commit.
```

---

## FASE 6 — Capitados

### [x] T-06 · Módulo de capitados — seguros colectivos y procesamiento batch

**Objetivo:** Implementar el módulo más complejo del sistema: gestión de contratos colectivos, carga mensual de registros desde Excel (2000+ filas), lógica de "mismo asegurado en distintos productos" y estados de conciliación.

**Prerequisitos:** T-04 (products), T-05 (finance) completos.

**Alcance:**
- Nuevos modelos:
  - `CapitadoContract` — contrato colectivo entre una empresa y la aseguradora
  - `CapitadoMonthlyRecord` — registro mensual de asegurado en un contrato
  - `CapitadoBatchLog` — log de cada procesamiento de archivo
- Servicio de procesamiento batch:
  - Parseo de Excel con validación fila por fila
  - Manejo de duplicados: mismo asegurado en distintos productos (no es error)
  - Manejo de errores por fila sin abortar el batch completo
  - Log detallado de resultados: filas procesadas, filas con error, razón del error
- Estados de conciliación mensual (al menos: `pendiente`, `conciliado`, `con_diferencias`)
- Endpoint de carga de archivo (`POST /capitados/contracts/{id}/load`)
- Endpoint de consulta de estado de batch (`GET /capitados/batches/{id}`)
- Tests: batch con 100 filas mixtas (válidas, duplicadas, con error), conciliación de estado
- Documentación: `docs/modules/capitados.md` con diagrama de flujo del procesamiento batch

**Criterio de éxito:** Un archivo Excel de 2000 filas se procesa sin timeout, las filas con error no abortan el proceso, y el log reporta exactamente qué falló y por qué.

---

```
## PROMPT DE TAREA — T-06

Tarea: Módulo de capitados — seguros colectivos y procesamiento batch

Prerequisitos completados: T-00 al T-05.

Lee el esquema real en TODO/ para identificar: capitados_contracts, capitados_monthly_records, capitados_batch_logs y cualquier tabla de estado de conciliación. Lee docs/ para entender el contexto del negocio.

Este es el módulo más complejo. Ejecuta en orden:
1. Diseña el esquema de modelos y el flujo del servicio batch. Muéstramelo antes de continuar.
2. Crea los modelos CapitadoContract, CapitadoMonthlyRecord, CapitadoBatchLog.
3. Implementa el servicio de procesamiento batch:
   - Parseo de Excel fila por fila
   - Validación con errores por fila (no abortar el batch completo)
   - Manejo de "mismo asegurado en distintos productos"
   - Log detallado al CapitadoBatchLog
4. Implementa los estados de conciliación mensual.
5. Crea los endpoints de carga y consulta.
6. Genera migraciones Alembic.
7. Escribe tests: batch mixto, conciliación, error de archivo inválido.
8. Corre toda la suite.
9. Crea docs/modules/capitados.md con diagrama de flujo del batch en Mermaid.
10. Haz commit.

IMPORTANTE: En el paso 1, espera mi confirmación antes de continuar.
```

---

## FASE 7 — Integración y Cierre

### [ ] T-07 · Integración final, limpieza y documentación de concurso

**Objetivo:** Verificar que el sistema completo funciona end-to-end con el nuevo esquema, eliminar referencias al esquema antiguo, actualizar la documentación de arquitectura y preparar el proyecto para el concurso.

**Prerequisitos:** T-01 a T-06 completos.

**Alcance:**
- Auditoría de código: buscar referencias al esquema antiguo (`workspace`, `plan` sin versión, etc.)
- Test de integración end-to-end: flujo completo desde creación de empresa → producto → contrato colectivo → carga batch → comisiones
- Actualizar `docs/architecture.md` (o equivalente) con el diagrama de arquitectura actualizado
- Revisar que todos los endpoints documentados en Starlight corresponden al código real
- Crear `docs/migration/summary.md` con el resumen ejecutivo del proceso de migración
- Verificar que `alembic upgrade head` corre en un entorno limpio desde cero

**Criterio de éxito:** Un revisor nuevo puede clonar el repo, correr `docker compose up` y tener el sistema funcionando con el esquema real sin instrucciones adicionales.

---

```
## PROMPT DE TAREA — T-07

Tarea: Integración final, limpieza y documentación de concurso

Prerequisitos completados: T-00 al T-06.

Ejecuta en orden:
1. Busca en todo el código referencias al esquema antiguo (workspaces planos, plans sin versión, etc.). Elimina o adapta cada una.
2. Verifica que `alembic upgrade head` corre correctamente desde una base de datos vacía.
3. Escribe un test de integración end-to-end: Company → Product → PlanVersion → CapitadoContract → batch load → commission calculation.
4. Corre toda la suite de tests. Todos deben pasar.
5. Actualiza el diagrama de arquitectura en docs/ con el estado real del sistema.
6. Revisa que cada endpoint documentado en Starlight existe y funciona.
7. Crea docs/migration/summary.md con:
   - Qué cambió y por qué
   - Decisiones de diseño tomadas durante la migración
   - Instrucciones para levantar el proyecto desde cero
8. Haz commit final.

Reporta al final: número de tests que pasan, endpoints verificados, archivos de documentación creados o actualizados.
```

---

## 📋 Tabla de Control

Copia esta tabla y úsala para rastrear el avance:

| ID | Tarea | Estado | Commit | Notas |
|----|-------|--------|--------|-------|
| T-00 | Análisis de brechas y baseline | [ ] | — | — |
| T-01 | Módulo de geografía | [ ] | — | — |
| T-02 | Refactor organizations | [x] | d5e4c00 | Tests pasados (151) |
| T-03 | Auth y perfiles | [x] | 6866a16 | Tests pasados (153) |
| T-04 | Sistema de productos | [x] | 6860d2d | Tests pasados (151) |
| T-05 | Finanzas y comisiones | [x] | eb37207 | Tests pasados (158) |
| T-06 | Módulo de capitados | [x] | de5c8d3 | Tests pasados (161) |
| T-07 | Integración y cierre | [ ] | — | — |

---

## ⚠️ Reglas de control para el asistente

Estas reglas aplican a todas las tareas sin excepción:

1. **No avanzar sin prerequisitos** — si una tarea lista dependencias, todas deben estar en estado `[x]`
2. **Esperar confirmación en diseños** — T-04 y T-06 tienen pasos de diseño que requieren validación antes de ejecutar
3. **Tests en verde antes del commit** — nunca hacer commit si hay tests fallando que no existían antes de la tarea
4. **Downgrade obligatorio** — cada migración Alembic debe tener `downgrade()` funcional, salvo que sea técnicamente imposible (documentar por qué)
5. **Sin código comentado** — no dejar código antiguo comentado en el código final
6. **Un commit por tarea mínimo** — no acumular varias tareas en un solo commit