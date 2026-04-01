import uuid
import google.generativeai as genai
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.modules.ai.models import KnowledgeDocument, ChatConversation, ChatMessage


class AIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.embedding_model = "models/gemini-embedding-001"

    def _should_handoff(
        self, user_message: str, assistant_text: str
    ) -> tuple[bool, str]:
        """Detección híbrida para transferencia a humano."""
        KEYWORDS_HANDOFF = [
            "humano",
            "agente",
            "asesor",
            "persona real",
            "hablar con alguien",
            "no eres humano",
        ]
        PHRASES_UNCERTAIN = [
            "lo siento, no puedo",
            "no tengo información",
            "te recomiendo contactar",
            "está fuera de mi alcance",
        ]

        u_msg = user_message.lower()
        if any(kw in u_msg for kw in KEYWORDS_HANDOFF):
            return True, "user_requested"

        a_txt = assistant_text.lower()
        if any(ph in a_txt for ph in PHRASES_UNCERTAIN):
            return True, "bot_uncertain"

        return False, ""

    async def generate_embedding(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self.embedding_model, content=text, task_type="retrieval_document"
        )
        return result["embedding"]

    async def get_relevant_documents(
        self, db: AsyncSession, company_id: uuid.UUID, query: str, limit: int = 5
    ) -> List[KnowledgeDocument]:
        # Generate embedding for the query
        query_embedding = await self.generate_embedding(query)

        # Search using Cosine Similarity (pgvector <-> operator)
        stmt = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.company_id == company_id)
            .order_by(KnowledgeDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def chat_with_context(
        self,
        db: AsyncSession,
        company_id: uuid.UUID,
        session_id: Optional[str],
        message: str,
    ) -> str:
        # 1. Find or create the conversation for this session
        final_session_id = session_id or str(uuid.uuid4())
        conv_res = await db.execute(
            select(ChatConversation).where(
                ChatConversation.session_id == final_session_id
            )
        )
        conversation = conv_res.scalar_one_or_none()
        if not conversation:
            conversation = ChatConversation(
                company_id=company_id, session_id=final_session_id
            )
            db.add(conversation)
            await db.flush()

        # 2. Persist the incoming user message
        user_msg = ChatMessage(
            conversation_id=conversation.id, role="user", content=message
        )
        db.add(user_msg)
        await db.flush()

        from app.core.events import notify_n8n

        await notify_n8n(
            "COMMENT_RECEIVED",
            {
                "conversation_id": str(conversation.id),
                "message": message,
                "sentiment_hint": None,
                "channel": "WEB_CHAT",
            },
        )

        # 3. Retrieve recent history (last 10 messages) for context
        history_res = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        recent_messages = list(reversed(history_res.scalars().all()))
        history_text = "\n".join(
            [f"{m.role.capitalize()}: {m.content}" for m in recent_messages[:-1]]
        )

        # 4. Get relevant docs (RAG)
        docs = await self.get_relevant_documents(db, company_id, message)
        context = "\n".join([f"Source: {d.title}\nContent: {d.content}" for d in docs])

        # 5. Build prompt with history and RAG context
        system_prompt = f"""Eres un asistente inteligente para la plataforma Yastubo.
Utiliza el siguiente contexto para responder a la pregunta del usuario.
Si la información no está en el contexto, indícalo educadamente.

CONTEXTO:
{context}"""

        history_section = (
            f"\n\nHISTORIAL PREVIO:\n{history_text}" if history_text else ""
        )
        full_prompt = (
            f"{system_prompt}{history_section}\n\nUsuario: {message}\nAsistente:"
        )

        # 6. Call Gemini
        response = await self.model.generate_content_async(full_prompt)
        assistant_text = response.text

        # 7. Handoff Detection & Event
        should_transfer, reason = self._should_handoff(message, assistant_text)
        if should_transfer:
            await notify_n8n(
                "AGENT_HANDOFF_REQUIRED",
                {
                    "conversation_id": str(conversation.id),
                    "company_id": str(company_id),
                    "reason": reason,
                    "last_user_message": message,
                    "last_bot_response": assistant_text,
                    "confidence_score": 0.0,
                },
            )

        # 8. Persist the assistant response
        assistant_msg = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_text,
        )
        db.add(assistant_msg)
        await db.commit()

        return assistant_text, conversation.session_id

    async def voice_chat(self, text: str) -> str:
        """Simple AI response for voice calls with specialized instructions."""
        system_prompt = """Eres el asistente de voz de Yastubo.
        Tu tono debe ser amable, empático y profesional.
        Responde de forma concisa (máximo 2 frases) ya que el usuario está escuchando por teléfono.
        Evita usar markdown o símbolos especiales."""

        prompt = f"{system_prompt}\n\nUsuario dice: {text}\nAsistente de voz:"
        response = await self.model.generate_content_async(prompt)
        return response.text


_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(api_key=settings.GOOGLE_API_KEY)
    return _ai_service
