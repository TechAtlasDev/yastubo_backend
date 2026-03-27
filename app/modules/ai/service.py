import uuid
import google.generativeai as genai
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.modules.ai.models import KnowledgeDocument


class AIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.embedding_model = "models/text-embedding-004"

    async def generate_embedding(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self.embedding_model, content=text, task_type="retrieval_document"
        )
        return result["embedding"]

    async def get_relevant_documents(
        self, db: AsyncSession, workspace_id: uuid.UUID, query: str, limit: int = 5
    ) -> List[KnowledgeDocument]:
        # Generate embedding for the query
        query_embedding = await self.generate_embedding(query)

        # Search using Cosine Similarity (pgvector <-> operator)
        # Note: In pgvector, <=> is cosine distance, <-> is Euclidean, <#> is negative dot product.
        # SQLAlchemy pgvector provides .cosine_distance()
        stmt = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.workspace_id == workspace_id)
            .order_by(KnowledgeDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def chat_with_context(
        self, db: AsyncSession, workspace_id: uuid.UUID, session_id: str, message: str
    ) -> str:
        # 1. Get relevant docs (RAG)
        docs = await self.get_relevant_documents(db, workspace_id, message)
        context = "\n".join([f"Source: {d.title}\nContent: {d.content}" for d in docs])

        # 2. Build system prompt
        system_prompt = f"""
        Eres un asistente inteligente para la plataforma Yastubo. 
        Utiliza el siguiente contexto para responder a la pregunta del usuario.
        Si la información no está en el contexto, indícalo educadamente.
        
        CONTEXTO:
        {context}
        """

        # 3. Call Gemini
        # For simplicity in this MVP, we pass context in the prompt.
        # For production, we should handle history in ChatConversation model.
        full_prompt = f"{system_prompt}\n\nUsuario: {message}\nAsistente:"
        response = await self.model.generate_content_async(full_prompt)

        # 4. Save message (optional: save history)
        # TODO: Implement full history management

        return response.text


_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        # Assuming GOOGLE_API_KEY is in settings
        _ai_service = AIService(api_key=settings.GOOGLE_API_KEY)
    return _ai_service
