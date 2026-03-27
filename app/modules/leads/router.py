import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.leads import service, schemas
from app.modules.leads.models import LeadStatus
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post(
    "/", response_model=schemas.LeadResponse, status_code=status.HTTP_201_CREATED
)
async def create_or_update_lead(
    data: schemas.LeadCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new lead or update an existing one based on phone_e164 (Matching key).
    This endpoint is public to allow lead capture from WhatsApp/Webhooks.
    """
    return await service.create_or_update_lead(db, data)


@router.get("/", response_model=List[schemas.LeadResponse])
async def list_leads(
    status: Optional[LeadStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all leads. Admin/Agent access only."""
    return await service.list_leads(db, status)


@router.get("/{lead_id}", response_model=schemas.LeadResponse)
async def get_lead(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get lead details by ID."""
    return await service.get_lead(db, lead_id)


@router.patch("/{lead_id}", response_model=schemas.LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    data: schemas.LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update lead status, funnel stage or checkout info."""
    return await service.update_lead(db, lead_id, data)
