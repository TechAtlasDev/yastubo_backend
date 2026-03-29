---
title: IA y RAG (Asistente Inteligente)
description: Documentación del módulo de Inteligencia Artificial, RAG y gestión de historial conversacional.
---

El módulo de IA de Yastubo utiliza el modelo **Gemini 1.5 Flash** para proporcionar asistencia inteligente a los usuarios y administradores, integrando capacidades de **RAG (Retrieval-Augmented Generation)** y gestión de historial.

## Arquitectura del Módulo AI

### 1. Ingesta de Conocimiento (`KnowledgeDocument`)
Los documentos de conocimiento se almacenan en la tabla `knowledge_documents` con sus respectivos embeddings generados por `text-embedding-004`.
*   **Vector Database**: Utilizamos la extensión `pgvector` de PostgreSQL para realizar búsquedas de similitud de coseno.
*   **RAG**: Antes de cada respuesta, el sistema busca los fragmentos más relevantes para inyectarlos en el prompt del sistema.

### 2. Gestión de Historial (`ChatConversation` & `ChatMessage`)
A diferencia de implementaciones básicas, Yastubo mantiene el contexto de la conversación:
*   **Persistencia**: Cada mensaje (usuario y asistente) se guarda en la base de datos vinculado a una `session_id`.
*   **Contexto Multi-turno**: El servicio recupera los últimos **10 mensajes** de la conversación para incluirlos en el prompt enviado a Gemini, permitiendo referencias a mensajes anteriores ("¿puedes explicarme más sobre el segundo punto?").
*   **Ordenamiento**: Se utiliza un ordenamiento determinista por `created_at` e `id` para garantizar la coherencia del diálogo.

## Endpoints Principales

### `POST /ai/chat`
Envía un mensaje al asistente dentro de una sesión específica.
*   **Input**: `session_id`, `message`.
*   **Proceso**:
    1.  Identifica o crea la `ChatConversation`.
    2.  Persiste el mensaje del usuario.
    3.  Busca documentos relevantes (RAG).
    4.  Recupera historial reciente.
    5.  Genera respuesta con Gemini.
    6.  Persiste y retorna la respuesta del asistente.

## Consideraciones Técnicas
*   **Embeddings**: 768 dimensiones.
*   **Modelo**: `gemini-1.5-flash`.
*   **Aislamiento**: Los documentos de conocimiento están aislados por `workspace_id`.
