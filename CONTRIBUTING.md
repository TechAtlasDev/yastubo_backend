# Guía de Contribución de Arquitectura - Yastubo Backend

¡Bienvenido, desarrollador! Antes de escribir tu primera línea de código en Yastubo, es **obligatorio** comprender nuestro modelo de **Monolito Modular**. Aquí no solo "añadimos código", construimos una plataforma escalable y auditable.

## 1. El Monolito Modular: La Regla de Oro
Yastubo no es un espagueti de archivos; es un conjunto de **dominios aislados** dentro de `app/modules/`.

*   **Aislamiento:** Un módulo (ej. `payments`) **nunca** debe importar modelos de otro módulo directamente para hacer queries.
*   **Comunicación:** Si el módulo `emission` necesita algo de `plans`, debe usar el **Service** de `plans` (`from app.modules.plans import service as plans_service`).
*   **Base de Datos:** Prohibido hacer "Joins" entre tablas de diferentes módulos en la capa de persistencia. La agregación de datos se hace en la capa de **Service**.

## 2. Estructura Obligatoria de un Módulo
Cada nuevo módulo debe seguir estrictamente este patrón de archivos:

```text
app/modules/mi_modulo/
├── __init__.py
├── models.py   # Solo definiciones de SQLAlchemy (BaseModel)
├── schemas.py  # Solo validaciones de Pydantic (In/Out)
├── service.py  # Lógica de negocio pura y orquestación
└── router.py   # Endpoints FastAPI y dependencias de Auth
```

## 3. Reglas de Asincronía y Rendimiento
Somos una API de alto rendimiento.
*   **Async/Await:** Todas las operaciones de I/O (DB, Redis, API Externas) **deben** ser asíncronas.
*   **Evitar Bloqueos:** Si una tarea es pesada (ej. enviar 1000 emails), no la hagas en el `service.py`. Usa el módulo de `workers` (ARQ).
*   **Non-blocking CRM:** Las sincronizaciones con Zoho deben ser "best-effort" y no bloquear la respuesta al usuario (`asyncio.create_task`).

## 4. Trazabilidad y Auditoría
Cualquier acción que cambie el estado de una entidad (Póliza, Cliente, Plan) **debe** estar auditada.
*   Usa el decorador `@audited(action="MI_ACCION", entity="MiEntidad")` en el método del `service.py`.
*   Asegúrate de pasar el `db: AsyncSession` y el `user_id` correspondiente al método.

## 5. El Motor de Estados
Si tu funcionalidad implica un flujo (ej. una Póliza que pasa de DRAFT a ACTIVE):
*   Define los estados en `state_machine.py` dentro del módulo.
*   Usa la función `transition()` para validar que el cambio sea legal.
*   Registra siempre el cambio en la tabla de `status_history`.

## 6. Pruebas y Calidad (Zero Regression)
No aceptamos código sin pruebas.
*   **Ubicación:** Cada módulo tiene su espejo en `tests/modules/mi_modulo/`.
*   **Integración:** Usa el `client` de FastAPI para probar el flujo completo (Request -> Service -> DB -> Response).
*   **Linting:** Si `make lint` (Ruff) falla, tu PR será rechazado automáticamente por el CI.

## 7. Flujo de Git
1. Rama desde `develop`.
2. Commit con formato Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`).
3. **Quality Gate Local:** Antes de subir, corre `make build`. Si no está en verde, no subas.

---
**Filosofía:** "Escribe código para que el próximo arquitecto que lo lea, no quiera cazarte".
