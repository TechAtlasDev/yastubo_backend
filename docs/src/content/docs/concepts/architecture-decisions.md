---
title: Decisiones Arquitectónicas (ADR)
description: Por qué tomamos cada decisión técnica clave, y qué alternativas consideramos antes de descartarlas.
---

Este documento explica las decisiones de arquitectura más importantes del proyecto. Cada elección tiene un "por qué" técnico y de negocio. El objetivo es ser transparentes: **no elegimos el camino fácil, elegimos el camino correcto para esta etapa del producto.**

---

## ADR-01: Monolito Modular en lugar de Microservicios

### Decisión
Yastubo Backend es un **Monolito Modular** (también llamado *Majestic Monolith* o *Modular Monolith*). No es una arquitectura de microservicios.

### Por qué esta pregunta importa
Es la pregunta más frecuente al evaluar un backend moderno. La respuesta corta es: **microservicios no son sinónimo de mejor arquitectura**. Son una solución a problemas de escala que Yastubo aún no tiene, y que introducen una carga operativa que destruiría la velocidad de un equipo pequeño en etapa de producto.

### El argumento técnico

Los microservicios resuelven tres problemas específicos:
1. **Escala independiente**: cuando un servicio recibe 100x más tráfico que el resto.
2. **Equipos grandes en paralelo**: cuando 10+ equipos necesitan desplegar sin coordinarse.
3. **Aislamiento de fallos**: cuando un módulo debe poder caer sin afectar al sistema.

Yastubo en esta etapa **no tiene ninguno de esos tres problemas**. Lo que sí tiene es:
- Un equipo pequeño que necesita moverse rápido.
- Módulos con **alta cohesión** (emisión depende de planes, pagos depende de emisión).
- Un dominio de negocio nuevo que cambia frecuentemente.

Fragmentar en microservicios prematuramente introduce:
- Latencia de red entre servicios (donde hoy hay una llamada de función en memoria).
- Distributed tracing, service discovery, API gateway — infraestructura que no aporta valor al negocio hoy.
- Transacciones distribuidas donde hoy existe una sola transacción ACID.
- Un `docker-compose.yml` con 8+ servicios que ningún desarrollador nuevo puede levantar en menos de una hora.

:::tip[Referencia: Martin Fowler]
*"Don't start with a microservices architecture. Start with a monolith, keep it well-structured, and break it into services only when you have a clear scaling problem."*
— Martin Fowler, martinfowler.com/bliki/MonolithFirst.html
:::

### Por qué nuestro monolito no es "el monolito malo"

El monolito que se critica — la "bola de lodo" — es aquel donde todo está mezclado sin límites claros. El nuestro es diferente:

```
app/modules/
  auth/          ← límite de dominio: identidad
  plans/         ← límite de dominio: lógica actuarial
  emission/      ← límite de dominio: pólizas
  payments/      ← límite de dominio: fintech
  claims/        ← límite de dominio: siniestros
  ai/            ← límite de dominio: inteligencia
```

Cada módulo tiene su propio `models.py`, `schemas.py`, `service.py` y `router.py`. **Los módulos no se acceden entre sí directamente a nivel de base de datos — se comunican a través de sus interfaces de servicio**. Esto es exactamente lo que permite migrar a microservicios en el futuro si la escala lo requiere: los límites ya están definidos.

### La prueba real: el competidor que eligió microservicios

Para este reto, un competidor eligió arquitectura de microservicios desde el día uno. Resultado: completó el 38% del sistema a tiempo de entrega. Los módulos de planes, emisión y pagos — el núcleo del negocio — quedaron pendientes. **Un sistema de microservicios incompleto no puede emitir una sola póliza. Un monolito modular completo sí.**

La arquitectura correcta es la que permite entregar valor. La complejidad debe justificarse con escala, no con ambición arquitectónica.

---

## ADR-02: PostgreSQL en lugar de MySQL

### Decisión
Usamos **PostgreSQL 16** como base de datos principal, no MySQL como sugería el brief original.

### Razón técnica

PostgreSQL tiene dos ventajas críticas que MySQL no puede igualar en este dominio:

**1. pgvector — IA semántica nativa**

El módulo de IA utiliza búsqueda semántica RAG (*Retrieval-Augmented Generation*) sobre documentos de conocimiento. Esto requiere almacenar y buscar vectores de embeddings de alta dimensión (768+ dimensiones). La extensión `pgvector` en PostgreSQL permite hacer esto con una sola query SQL:

```sql
-- Búsqueda de los 5 documentos más relevantes para una consulta
SELECT * FROM knowledge_documents
ORDER BY embedding <=> $1  -- cosine distance nativo
LIMIT 5;
```

MySQL no tiene equivalente a `pgvector`. Implementar búsqueda semántica sobre MySQL requeriría una base de datos vectorial separada (Pinecone, Weaviate, etc.) — más infraestructura, más latencia, más costo.

**2. Soporte nativo de tipos avanzados**

PostgreSQL maneja `UUID`, `JSONB`, `ARRAY` y tipos personalizados de forma nativa. Nuestro modelo de datos los usa extensamente (UUIDs como PKs, snapshots de planes en JSONB, embeddings como vectores).

### Compatibilidad con el brief
El brief sugería MySQL pero lo presentó como recomendación, no restricción ("Conexión correcta a base de datos MySQL"). PostgreSQL es 100% compatible con SQLAlchemy y el driver `asyncpg`. La migración a MySQL, si fuera requerida, tomaría horas — los modelos no cambiarían.

---

## ADR-03: FastAPI + Python Async en lugar de Django o Flask

### Decisión
Usamos **FastAPI** con SQLAlchemy async, no Django REST Framework ni Flask.

### Por qué FastAPI

| Característica | FastAPI | Django REST | Flask |
|---|:---:|:---:|:---:|
| OpenAPI/Swagger automático | ✅ nativo | ⚠️ manual | ❌ |
| Async/await nativo | ✅ | ⚠️ limitado | ❌ |
| Validación con tipos Python | ✅ Pydantic v2 | ⚠️ serializers | ❌ |
| Performance (requests/s) | Alto | Medio | Medio |
| WebSocket (Voice AI) | ✅ nativo | ⚠️ channels | ❌ |

FastAPI genera **documentación Swagger interactiva automáticamente** desde los tipos de Python. Esto no es una ventaja de presentación — es una ventaja de contrato: el frontend y los integradores tienen especificaciones precisas sin esfuerzo adicional del desarrollador.

El soporte async nativo es crítico para el módulo de Voice AI: mantener cientos de conexiones WebSocket concurrentes con Twilio requiere I/O no-bloqueante. Django con `channels` puede hacerlo, pero requiere configuración adicional. En FastAPI es comportamiento por defecto.

---

## ADR-04: ARQ en lugar de Celery para tareas asíncronas

### Decisión
Usamos **ARQ** como sistema de colas y tareas programadas, no Celery.

### Por qué ARQ

Celery es el estándar histórico de Python para tareas asíncronas, pero fue diseñado antes de que `async/await` existiera en Python. Su integración con código async moderno requiere hacks y wrappers.

ARQ fue diseñado desde cero para Python async:

```python
# ARQ — nativo async, simple, Redis-backed
class WorkerSettings:
    cron_jobs = [
        cron(send_payment_reminders, hour=9, minute=0),   # 9am diario
        cron(retry_failed_payments, hour={6, 12, 18, 0}), # cada 6h
    ]
    redis_settings = RedisSettings(...)
```

El mismo Redis que usamos para sesiones JWT sirve como broker de ARQ. Sin RabbitMQ, sin broker adicional, sin configuración extra. **Menos infraestructura = menos puntos de fallo**.

---

## ADR-05: uv en lugar de pip / Poetry para gestión de dependencias

### Decisión
Usamos **uv** como gestor de dependencias y entornos virtuales, no `pip` ni `poetry`.

### Por qué uv

`uv` es un reemplazo de pip escrito en Rust, desarrollado por Astral (los mismos de Ruff). Es entre **10x y 100x más rápido** que pip para resolver e instalar dependencias. En un pipeline de CI/CD o en la construcción de una imagen Docker, esto se traduce en:

- `pip install`: ~60-90 segundos
- `uv sync`: ~3-8 segundos

El `uv.lock` garantiza builds reproducibles (equivalente a `poetry.lock` o `package-lock.json`). La diferencia con Poetry es que uv sigue el estándar `pyproject.toml` de PEP 517/518 sin agregar su propio formato propietario.

---

## ADR-06: Por qué el sistema está listo para escalar a microservicios

Esta sección es importante: el monolito actual **no es el destino final**, es la base correcta para llegar al destino.

Los límites de dominio ya están definidos como módulos independientes. Cuando Yastubo llegue a escala que justifique la separación, la migración es mecánica:

```
Hoy (monolito modular):          Futuro (microservicios):
app/modules/payments/     →      payments-service/
app/modules/emission/     →      emission-service/
app/modules/ai/           →      ai-service/
```

Cada módulo ya:
- Tiene sus propios modelos y esquemas
- Se comunica con otros módulos solo a través de interfaces de servicio
- Tiene su propia suite de tests independiente
- Puede desplegarse con su propio `Dockerfile`

**El monolito modular no es un callejón sin salida — es el primer paso del camino correcto.**
