import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from loguru import logger

from app.modules.leads.models import Lead, LeadStatus, FunnelStage
from app.modules.leads.schemas import LeadCreate, LeadUpdate
from app.core.events import dispatch_event_background


async def create_or_update_lead(db: AsyncSession, data: LeadCreate) -> Lead:
    """
    Gold Rule: Never create two records with same phone_e164.
    If phone exists, update the existing lead with new attribution/data.
    """
    # 1. Deduplication check
    existing = await db.execute(select(Lead).where(Lead.phone_e164 == data.phone_e164))
    lead = existing.scalar_one_or_none()

    if lead:
        logger.info(f"Existing lead found for {data.phone_e164}. Updating data.")
        # Update existing lead with new data (if not null)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, key, value)
        lead.updated_at = datetime.now()
        dispatch_event_background(
            "LEAD_UPDATED", {"lead_id": str(lead.id), "phone": lead.phone_e164}
        )
    else:
        logger.info(f"Creating new lead for {data.phone_e164}.")
        insert_data = data.model_dump()
        if insert_data.get("workspace_id") is None:
            # Fallback to first available workspace (usually one in this project)
            from app.modules.workspaces.models import Workspace

            res = await db.execute(select(Workspace.id).limit(1))
            insertion_ws = res.scalar_one_or_none()
            if not insertion_ws:
                raise HTTPException(
                    status_code=400, detail="No workspace found in system."
                )
            insert_data["workspace_id"] = insertion_ws

        lead = Lead(**insert_data)
        lead.first_contact_at = datetime.now()
        db.add(lead)
        await db.flush()  # Ensure ID is generated for event
        dispatch_event_background(
            "LEAD_CREATED", {"lead_id": str(lead.id), "phone": lead.phone_e164}
        )

    await db.commit()
    await db.refresh(lead)
    return lead


async def get_lead(db: AsyncSession, lead_id: uuid.UUID) -> Lead:
    res = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


async def update_lead(db: AsyncSession, lead_id: uuid.UUID, data: LeadUpdate) -> Lead:
    lead = await get_lead(db, lead_id)

    # Track checkout state changes
    if data.checkout_started and not lead.checkout_started:
        lead.checkout_started_at = datetime.now()
        lead.funnel_stage = FunnelStage.INTENT

    if data.abandoned_checkout_flag and not lead.abandoned_checkout_flag:
        lead.abandoned_checkout_at = datetime.now()

    if data.purchase_completed and not lead.purchase_completed:
        lead.lead_status = LeadStatus.CONVERTED
        lead.funnel_stage = FunnelStage.PURCHASE
        lead.checkout_completed = True
        lead.converted_to_contact_flag = True
        lead.converted_at = datetime.now()

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)

    await db.commit()
    await db.refresh(lead)
    return lead


async def list_leads(
    db: AsyncSession, status: Optional[LeadStatus] = None
) -> List[Lead]:
    query = select(Lead).order_by(Lead.created_at.desc())
    if status:
        query = query.where(Lead.lead_status == status)

    res = await db.execute(query)
    return list(res.scalars().all())
