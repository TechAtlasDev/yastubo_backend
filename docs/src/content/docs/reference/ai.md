---
title: AI (Inteligencia Aplicada)
description: Modelos generativos, embeddings y motor de RAG para soporte inteligente.
---

El módulo de **AI** de Yastubo integra capacidades de inteligencia artificial generativa de última generación para potenciar el soporte al cliente y la toma de decisiones basada en datos. Utiliza modelos de **Google Gemini** para ofrecer un asistente contextualizado y preciso.

## Key Features

*   **RAG (Retrieval-Augmented Generation)**: Mejora las respuestas de la IA inyectando contexto relevante de documentos internos.
*   **Gestión de Embeddings**: Conversión de texto en vectores numéricos para búsquedas semánticas de alta precisión.
*   **Memoria de Conversación**: Seguimiento del historial de chat por sesión para interacciones naturales.
*   **Motor pgvector**: Almacenamiento y búsqueda eficiente de vectores directamente en la base de datos PostgreSQL.

:::tip[Eficiencia de IA]
Utilizamos el modelo `gemini-1.5-flash` por su equilibrio perfecto entre velocidad de respuesta, ventana de contexto masiva y bajo costo operativo.
:::

## Deep Dive Técnico

### El Proceso RAG (Retrieval-Augmented Generation)
Para evitar "alucinaciones" y asegurar que la IA responda basándose en los planes y términos legales de Yastubo, el flujo es el siguiente:

1.  **Input**: El usuario envía una pregunta.
2.  **Embedding**: La pregunta se convierte en un vector usando `text-embedding-004`.
3.  **Búsqueda Semántica**: Se realiza una búsqueda en PostgreSQL usando el operador de distancia de coseno (`<=>`) sobre la tabla de documentos de conocimiento.
4.  **Prompt Dinámico**: Se construye un "System Prompt" que incluye los fragmentos de documentos encontrados.
5.  **Generación**: Gemini genera la respuesta final usando el contexto inyectado.

### Persistencia y Contexto
El sistema guarda cada mensaje de la conversación (`ChatMessage`) vinculado a una sesión (`ChatConversation`). En cada nueva pregunta, se recuperan los últimos 10 mensajes para mantener el hilo del diálogo.

## Ejemplo Práctico: Asistente con Contexto

El siguiente fragmento muestra cómo se orquestra la llamada a la IA integrando el contexto de la base de datos de conocimiento:

```python
async def chat_with_context(
    self, db: AsyncSession, workspace_id: uuid.UUID, session_id: str, message: str
) -> str:
    """
    Gestiona una sesión de chat inteligente aplicando RAG.
    """
    # 1. Recuperar documentos relevantes (Búsqueda semántica)
    docs = await self.get_relevant_documents(db, workspace_id, message)
    context = "\n".join([f"Fuente: {d.title}\nContenido: {d.content}" for d in docs])

    # 2. Construir el prompt de sistema con el conocimiento inyectado
    system_prompt = f"""
    Eres un experto en seguros de Yastubo. Responde solo basándote en el CONTEXTO.
    CONTEXTO:
    {context}
    """

    # 3. Consultar a Gemini con el prompt enriquecido
    response = await self.model.generate_content_async(
        f"{system_prompt}\nUsuario: {message}"
    )
    return response.text
```

## Diagrama de Proceso

> [FLOW: El usuario hace una pregunta. El sistema genera el embedding de la pregunta. Se realiza una búsqueda vectorial en la tabla KnowledgeDocument usando pgvector. Se extraen los 5 documentos más parecidos semánticamente. Se envía la pregunta + documentos + historial a Gemini. Gemini responde contextualmente. Se guarda la respuesta en la base de datos].

## Modelos Utilizados

| Tarea | Modelo | Proveedor |
| :--- | :--- | :--- |
| **Generación de Texto** | `gemini-1.5-flash` | Google Generative AI |
| **Embeddings** | `text-embedding-004` | Google Generative AI |
| **Base de Datos Vectorial** | `pgvector` | Extensión de PostgreSQL |
