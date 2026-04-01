1. Captación y Respuesta Directa (Social Media)
⚡ DM Automático desde Comentario con Keyword:

Funcionamiento: n8n capta un webhook de Meta (Instagram/FB) cuando un usuario comenta una palabra clave (ej. "INFO"). OpenAI personaliza la respuesta y envía un DM con un link trackeado (UTM) al funnel /activate.

Stack: n8n, OpenAI, Meta Graph API, Chatwoot.

⚡ Flujo de Calificación por Respuesta a Story:

Funcionamiento: Al reaccionar o responder a una Story, n8n intercepta el evento. Un Agent Bot en Chatwoot (vía OpenAI) realiza 3 preguntas de calificación (estado en EE.UU., país, plan actual).

Stack: n8n, Chatwoot, OpenAI, Meta Graph API.

⚡ DM de Bienvenida a Nuevos Seguidores:

Funcionamiento: n8n verifica periódicamente la lista de seguidores. Si detecta uno nuevo, OpenAI genera un mensaje de bienvenida humano para evitar flags de spam (límite de 50/hora).

Stack: n8n, OpenAI, Meta Graph API.

⚡ Auto-respuesta por Keywords en TikTok:

Funcionamiento: Configuración de respuestas automáticas en TikTok Business Suite para DMs con palabras clave, redirigiendo directamente al link de activación.

Stack: TikTok Business Suite, n8n (para flows avanzados).

Links en Bio con UTMs Dinámicos:

Funcionamiento: Rotación de URLs según la campaña activa para trazar el origen exacto del lead en Zoho CRM.

Stack: n8n, Zoho CRM.

2. Gestión Inteligente de Conversaciones
⚡ Agent Bot de Calificación (Chatwoot):

Funcionamiento: n8n actúa como cerebro del Agent Bot. Procesa cada mensaje entrante con OpenAI usando un system prompt específico de Yastubo para decidir si envía el link del funnel o escala a un humano.

Stack: Chatwoot, n8n, OpenAI.

⚡ Handoff a Agente Humano con Contexto:

Funcionamiento: Si OpenAI detecta una pregunta compleja o baja confianza en la respuesta (confianza < 0.7), cambia el estado de la conversación a "Abierto" en Chatwoot y notifica al equipo.

Stack: Chatwoot, n8n, OpenAI.

⚡ Etiquetado Automático de Conversaciones:

Funcionamiento: Aplicación de labels en Chatwoot (país, interés, etapa) mediante reglas de automatización y n8n según el contenido del chat.

Stack: Chatwoot, n8n.

Bandeja Unificada Omnicanal:

Funcionamiento: Centralización de DMs de IG y FB en una sola interfaz dentro de Chatwoot para evitar el acceso directo a las cuentas sociales.

Stack: Chatwoot Cloud.

Macros de Ejecución en 1 Clic:

Funcionamiento: Botones rápidos en Chatwoot para encadenar acciones: enviar link + poner label + cerrar chat.

Stack: Chatwoot.

3. Integración con CRM y Seguimiento
⚡ Creación Automática de Leads en Zoho CRM:

Funcionamiento: Al terminar la calificación en Chatwoot, n8n crea o actualiza el lead en Zoho CRM mapeando campos como "Lead Source" y ubicación.

Stack: n8n, Zoho CRM, Chatwoot.

⚡ Secuencia de Follow-up (Nurturing):

Funcionamiento: Si un lead recibió el link pero no activó en 48h, n8n dispara una secuencia de 4 mensajes (testimonios, urgencia, beneficios) vía DMs.

Stack: n8n, Chatwoot, OpenAI, Zoho CRM.

Reactivación de Leads Fríos:

Funcionamiento: Revisión semanal de leads inactivos por más de 14 días en Zoho CRM para enviar un mensaje de reenganche con un ángulo nuevo generado por OpenAI.

Stack: n8n, Zoho CRM, OpenAI, Chatwoot.

Sincronización en Tiempo Real Bidireccional:

Funcionamiento: n8n refleja cada cambio de estado (label aplicado, chat resuelto) de Chatwoot directamente en el pipeline de Zoho CRM.

Stack: n8n, Chatwoot, Zoho CRM.

4. Moderación y Análisis
⚡ Respuesta Automática a Comentarios Públicos:

Funcionamiento: n8n detecta preguntas frecuentes en posts (precio, cobertura), OpenAI responde públicamente e invita al usuario al DM simultáneamente.

Stack: n8n, OpenAI, Meta Graph API.

Moderación Proactiva de Sentimiento:

Funcionamiento: OpenAI evalúa el sentimiento de los comentarios nuevos; si detecta spam o negatividad, n8n los oculta automáticamente vía API.

Stack: n8n, OpenAI, Meta Graph API.

Respuesta a Comentarios en TikTok:

Funcionamiento: Respuestas automáticas de texto en el TikTok Business Center para invitar al usuario a los DMs (donde sí se permiten links).

Stack: TikTok Business Suite.

Reporte Semanal de KPIs:

Funcionamiento: Cada lunes, n8n compila métricas de todas las plataformas y genera un resumen ejecutivo con OpenAI que se envía por email.

Stack: n8n, Zoho CRM, Chatwoot, OpenAI.
