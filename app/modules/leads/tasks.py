import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.modules.leads.models import Lead, LeadStatus, FunnelStage
from app.modules.leads import service as leads_service
from app.modules.leads.schemas import LeadUpdate
from app.modules.emission.models import Policy
from app.modules.emission.state_machine import PolicyStatus
from app.core.database import SessionLocal

async def check_abandoned_checkouts() -> int:
    """
    Finds Policies in PENDING_PAYMENT status older than 24h
    and marks their linked Leads as abandoned.
    """
    count = 0
    limit_time = datetime.now() - timedelta(hours=24)
    
    async with SessionLocal() as db:
        # 1. Find policies pending for too long
        query = select(Policy).where(
            Policy.status == PolicyStatus.PENDING_PAYMENT,
            Policy.created_at < limit_time,
            Policy.lead_id.isnot(None)
        )
        res = await db.execute(query)
        policies = res.scalars().all()
        
        for policy in policies:
            # Check if lead is already marked as abandoned
            lead = await leads_service.get_lead(db, policy.lead_id)
            if not lead.abandoned_checkout_flag and not lead.purchase_completed:
                await leads_service.update_lead(
                    db, 
                    lead.id, 
                    LeadUpdate(abandoned_checkout_flag=True)
                )
                logger.info(f"Policy {policy.policy_number} identified as abandoned checkout. Lead {lead.id} updated.")
                count += 1
        
        await db.commit()
    
    return count

if __name__ == "__main__":
    # Manual run for debugging
    asyncio.run(check_abandoned_checkouts())
