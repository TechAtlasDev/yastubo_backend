import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.audit import service as audit_service
from app.modules.audit.schemas import PaginatedAuditResponse

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/", response_model=PaginatedAuditResponse)
async def get_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    entity_id: Optional[uuid.UUID] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: bool = Depends(require_role("ADMIN"))
):
    items, total = await audit_service.list_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size
    )
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
