---
title: Decisiones Arquitectónicas (ADR)
description: Registro de las decisiones técnicas clave del proyecto, con el contexto y razonamiento detrás de cada una.
---

Este documento registra las decisiones de arquitectura más relevantes del proyecto. Para cada una se describe el contexto, las alternativas evaluadas y el razonamiento técnico que llevó a la elección final.

---

## ADR-01: ¿Por qué no microservicios?

**Contexto**

Yastubo es un producto en etapa de crecimiento con un dominio de negocio que evoluciona rápidamente. Los módulos del sistema tienen alta cohesión: la emisión de pólizas depende del motor actuarial de planes, y los pagos dependen del estado de las pólizas. Esta interdependencia es intrínseca al negocio de seguros.

**Decisión**

Arquitectura de **Monolito Modular** con límites de dominio estrictos.

**Razonamiento**

Los microservicios resuelven problemas concretos de escala: despliegue independiente de componentes con patrones de carga muy distintos, y coordinación de equipos grandes que trabajan en paralelo. En la etapa actual, aplicar esa arquitectura introduciría costos operativos que no generan valor proporcional:

- Latencia de red en cada llamada entre servicios (hoy son llamadas de función en memoria dentro de una transacción ACID).
- Infraestructura adicional: service discovery, API gateway, distributed tracing.
- Complejidad de coordinación en transacciones que hoy son atómicas.

El patrón elegido captura los beneficios de organización de los microservicios — límites de dominio claros, separación de responsabilidades — sin la carga operativa prematura.

```
app/modules/
  auth/       # identidad y acceso
  plans/      # motor actuarial
  emission/   # pólizas y beneficiarios
  payments/   # Stripe y finanzas
  claims/     # siniestros
  ai/         # inteligencia y RAG
```

Cada módulo es autónomo: modelos, esquemas, servicios y router propios. Los módulos se comunican exclusivamente a través de sus interfaces de servicio, nunca accediendo directamente a las tablas del otro. Esto preserva la opción de extraer servicios individuales cuando la escala lo justifique — los límites ya están definidos.

:::tip[Referencia]
*"Don't start with a microservices architecture. Start with a monolith, keep it well-structured, and break it into services only when you have a clear scaling problem."*
— Martin Fowler, [MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)
:::

**Evolución prevista**

Cuando el volumen lo justifique, la extracción de servicios es directa:

```
app/modules/payments/  →  payments-service/
app/modules/ai/        →  ai-service/
```

Cada módulo ya tiene sus propios modelos, esquemas y tests. El `Dockerfile` del proyecto soporta esta extracción sin cambios de estructura.

---

## ADR-02: PostgreSQL como base de datos principal

**Contexto**

El sistema requiere dos capacidades que van más allá del almacenamiento relacional estándar: búsqueda semántica vectorial para el módulo de IA, y almacenamiento de snapshots de planes en formato flexible (los términos de una póliza no deben cambiar aunque el plan evolucione).

**Decisión**

**PostgreSQL 16** con la extensión `pgvector`.

**Razonamiento**

La extensión `pgvector` permite almacenar embeddings de alta dimensión y ejecutar búsqueda por similitud coseno directamente en SQL, sin infraestructura adicional:

```sql
SELECT * FROM knowledge_documents
ORDER BY embedding <=> $query_embedding
LIMIT 5;
```

Esta capacidad es la base del módulo de IA con RAG. Implementarla sobre otro motor requeriría una base de datos vectorial separada (Pinecone, Weaviate), añadiendo latencia de red y una dependencia externa.

PostgreSQL también ofrece soporte nativo de `UUID`, `JSONB` y tipos de array que el modelo de datos usa extensamente — snapshots de planes en JSONB, embeddings como vectores, UUIDs como claves primarias.

---

## ADR-03: FastAPI con SQLAlchemy async

**Contexto**

El sistema tiene dos patrones de I/O simultáneos: peticiones HTTP convencionales de la API REST, y conexiones WebSocket de larga duración para el módulo de Voice AI (stream bidireccional con Twilio).

**Decisión**

**FastAPI** + **SQLAlchemy 2.0 async** + **asyncpg**.

**Razonamiento**

FastAPI genera especificaciones OpenAPI 3.0 automáticamente a partir de las anotaciones de tipo de Python. Esto garantiza que la documentación Swagger esté siempre sincronizada con la implementación real — sin esfuerzo de mantenimiento adicional.

El modelo de concurrencia async/await de FastAPI permite manejar conexiones WebSocket de larga duración junto con peticiones HTTP sin bloquear el event loop. Esto es esencial para el módulo de Voice AI: un stream de audio con Twilio puede durar minutos, durante los cuales el servidor debe seguir atendiendo otras peticiones.

| Característica | FastAPI | Django REST | Flask |
|---|:---:|:---:|:---:|
| OpenAPI automático desde tipos | ✅ | ⚠️ extra | ❌ |
| Async/await nativo | ✅ | ⚠️ channels | ❌ |
| WebSocket sin configuración extra | ✅ | ❌ | ❌ |
| Validación con Pydantic v2 | ✅ | ❌ | ❌ |

---

## ADR-04: ARQ para tareas asíncronas y cron jobs

**Contexto**

El sistema ejecuta tareas programadas: recordatorios de pago a las 9am diarias, reintentos automáticos de cobros fallidos cada 6 horas, y detección de checkouts abandonados. Estas tareas deben integrarse con el mismo stack async del resto del sistema.

**Decisión**

**ARQ** como sistema de colas y tareas programadas, con Redis como broker.

**Razonamiento**

ARQ fue diseñado desde cero para Python async. Sus workers son corrutinas nativas, lo que permite reutilizar el mismo código de servicios async que usa la API sin adaptadores ni wrappers.

Usa el mismo Redis que ya gestiona las sesiones JWT, eliminando la necesidad de un broker de mensajes adicional (RabbitMQ, SQS). La configuración completa del worker es declarativa:

```python
class WorkerSettings:
    cron_jobs = [
        cron(send_payment_reminders, hour=9, minute=0),
        cron(retry_failed_payments, hour={6, 12, 18, 0}),
    ]
```

---

## ADR-05: uv como gestor de dependencias

**Contexto**

La velocidad de instalación de dependencias afecta directamente el tiempo de construcción de imágenes Docker en CI/CD y el tiempo de onboarding de nuevos desarrolladores.

**Decisión**

**uv** como gestor de paquetes y entornos virtuales.

**Razonamiento**

`uv` es un reemplazo de pip implementado en Rust por el equipo de Astral. Resuelve e instala dependencias entre 10x y 100x más rápido que pip, con resolución determinista garantizada por `uv.lock`.

Sigue el estándar `pyproject.toml` (PEP 517/518) sin introducir formatos propietarios, lo que mantiene la portabilidad del proyecto hacia cualquier herramienta compatible con el estándar.

```bash
# Tiempo típico de instalación desde cero
pip install -r requirements.txt  →  ~75 segundos
uv sync                          →  ~5 segundos
```
