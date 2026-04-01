---
title: AI (Inteligencia Aplicada)
description: Modelos generativos, embeddings y motor de RAG para soporte inteligente.
---

El módulo de **AI** de Yastubo integra capacidades de inteligencia artificial generativa de última generación para potenciar el soporte al cliente y la toma de decisiones basada en datos. Utiliza los modelos más recientes de **Google Gemini** para ofrecer un asistente contextualizado, preciso y de baja latencia.

## Key Features

*   **RAG (Retrieval-Augmented Generation)**: Mejora las respuestas de la IA inyectando contexto relevante recuperado de documentos internos y manuales de pólizas.
*   **Ingesta de Documentos PDF**: Procesamiento automatizado de archivos PDF para su conversión en conocimiento vectorial.
*   **Voice AI Support**: Interfaz especializada para llamadas telefónicas (Twilio + ElevenLabs) con respuestas optimizadas para ser escuchadas.
*   **Gestión de Embeddings de Alta Dimensión**: Uso de vectores de 3072 dimensiones para una precisión semántica superior.
*   **Memoria de Conversación**: Seguimiento del historial de chat por sesión para interacciones fluidas y naturales.

## Modelos y Configuración

| Tarea | Modelo | Detalles |
| :--- | :--- | :--- |
| **Generación de Texto** | `gemini-2.5-flash` | Alta velocidad, ventana de contexto masiva. |
| **Embeddings** | `gemini-embedding-001` | **3072 dimensiones** para máxima precisión semántica. |
| **Base de Datos Vectorial** | `pgvector` | Extensión de PostgreSQL integrada con SQLAlchemy. |

:::tip[Modelo de Vanguardia]
Yastubo utiliza **Gemini 2.5 Flash**, lo que permite manejar conversaciones complejas con una latencia mínima, ideal para aplicaciones en tiempo real como el asistente de voz.
:::

## El Proceso RAG (Retrieval-Augmented Generation)

Para evitar "alucinaciones" y asegurar respuestas basadas en datos reales, el flujo sigue estos pasos:

### 1. Ingesta de Conocimiento (Knowledge Ingestion)
Puedes cargar información en el sistema de dos formas:
*   **Texto Plano**: Enviando el contenido directamente al endpoint `/knowledge`.
*   **Documentos PDF**: Subiendo archivos al endpoint `/knowledge/upload`. El sistema extrae automáticamente el texto usando `pypdf`, genera los embeddings y los guarda en la base de datos.

### 2. Recuperación y Generación (Retrieval & Generation)
Cuando un usuario hace una pregunta:
1.  **Vectorización**: La pregunta se convierte en un vector de 3072 dimensiones.
2.  **Búsqueda Semántica**: Se realiza una búsqueda en PostgreSQL usando el operador de distancia de coseno (`<=>`).
3.  **Aumentación**: Los documentos más relevantes se inyectan en el prompt del sistema.
4.  **Respuesta**: Gemini genera el texto final basándose estrictamente en el contexto proporcionado.

## Ejemplo: Carga de Documentos (PDF)

El siguiente ejemplo muestra cómo subir una póliza PDF al sistema de conocimiento:

```bash
curl -X POST "https://api.yastubo.com/api/v1/ai/knowledge/upload" \
     -H "Authorization: Bearer <TOKEN>" \
     -F "file=@manual_poliza.pdf"
```

## Voice AI: Optimización para Telefonía

Para la integración con sistemas de voz, el módulo expone el método `voice_chat`. Este método aplica reglas de negocio específicas:
- **Concisión**: Respuestas de máximo 2 frases.
- **Limpieza**: Eliminación de markdown y caracteres especiales para una síntesis de voz (TTS) fluida.
- **Empatía**: Tono profesional pero cercano.

## Desarrollo y Pruebas

### Pruebas de Humo (Smoke Tests)
Para verificar la conectividad real con Google Gemini y la base de datos vectorial, el proyecto incluye un script de diagnóstico:

```bash
PYTHONPATH=. uv run python scripts/smoke_test_rag.py
```

Este script simula el ciclo completo: genera un PDF temporal, lo sube, lo vectoriza y realiza una pregunta de prueba para validar que la IA recupera el dato exacto.
