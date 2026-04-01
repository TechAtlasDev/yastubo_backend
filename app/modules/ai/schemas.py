import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class KnowledgeDocumentCreate(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None
    metadata_json: Optional[dict] = None


class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    content: str
    source_url: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
