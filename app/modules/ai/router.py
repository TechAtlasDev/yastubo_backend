import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pypdf import PdfReader
import io
from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    require_role,
    get_current_company_id,
)
from app.modules.auth.models import User
from app.modules.ai.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    ChatRequest,
    ChatResponse,
)
from app.modules.ai.service import get_ai_service, AIService
from app.modules.ai.models import KnowledgeDocument

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/knowledge/upload", response_model=KnowledgeDocumentResponse)
async def upload_knowledge_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company_id),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(require_role("ADMIN")),
):
    """Extrae texto de un PDF y lo carga en el sistema de conocimiento (RAG)."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer texto legible del PDF.",
            )

        # Generate embedding for the extracted text
        embedding = await ai_service.generate_embedding(extracted_text)

        doc = KnowledgeDocument(
            company_id=company_id,
            title=file.filename,
            content=extracted_text,
            embedding=embedding,
            metadata_json={"filename": file.filename, "size": len(content)},
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error procesando el PDF: {str(exc)}"
        )


@router.post("/knowledge", response_model=KnowledgeDocumentResponse)
async def create_knowledge_document(
    data: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company_id),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(require_role("ADMIN")),
):
    # Generate embedding for the document content
    embedding = await ai_service.generate_embedding(data.content)

    doc = KnowledgeDocument(
        company_id=company_id,
        title=data.title,
        content=data.content,
        source_url=data.source_url,
        metadata_json=data.metadata_json,
        embedding=embedding,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/knowledge", response_model=List[KnowledgeDocumentResponse])
async def list_knowledge_documents(
    db: AsyncSession = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company_id),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    from sqlalchemy import select

    res = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.company_id == company_id)
    )
    return list(res.scalars().all())


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company_id),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
):
    response_text, final_session_id = await ai_service.chat_with_context(
        db=db,
        company_id=company_id,
        session_id=data.session_id,
        message=data.message,
    )

    return ChatResponse(response=response_text, session_id=final_session_id)
