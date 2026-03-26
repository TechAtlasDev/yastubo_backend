import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role, get_current_workspace_id
from app.modules.auth.models import User
from app.modules.ai.schemas import KnowledgeDocumentCreate, KnowledgeDocumentResponse, ChatRequest, ChatResponse
from app.modules.ai.service import get_ai_service, AIService
from app.modules.ai.models import KnowledgeDocument

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/knowledge", response_model=KnowledgeDocumentResponse)
async def create_knowledge_document(
    data: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(require_role("ADMIN"))
):
    # Generate embedding for the document content
    embedding = await ai_service.generate_embedding(data.content)
    
    doc = KnowledgeDocument(
        workspace_id=workspace_id,
        title=data.title,
        content=data.content,
        source_url=data.source_url,
        metadata_json=data.metadata_json,
        embedding=embedding
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

@router.get("/knowledge", response_model=List[KnowledgeDocumentResponse])
async def list_knowledge_documents(
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    from sqlalchemy import select
    res = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.workspace_id == workspace_id))
    return list(res.scalars().all())

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user)
):
    response_text = await ai_service.chat_with_context(
        db=db,
        workspace_id=workspace_id,
        session_id=data.session_id,
        message=data.message
    )
    
    return ChatResponse(
        response=response_text,
        session_id=data.session_id
    )
