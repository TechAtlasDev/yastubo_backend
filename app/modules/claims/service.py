import json
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.modules.claims.models import Claim, ClaimExpense
from app.modules.claims.schemas import (
    ClaimCreate,
    ClaimUpdateStatus,
    ClaimExpenseCreate,
)
from app.modules.claims.state_machine import can_transition, ClaimStatus
from app.modules.audit.decorator import audited
from app.core.redis import redis_client


@audited(action="CREATE_CLAIM", entity="Claim")
async def create_claim(
    db: AsyncSession, claim_in: ClaimCreate, user_id: uuid.UUID
) -> Claim:
    new_claim = Claim(
        **claim_in.model_dump(),
        status=ClaimStatus.REPORTED,
        reported_at=datetime.utcnow(),
    )
    db.add(new_claim)
    await db.commit()

    # Reload with expenses to avoid lazy loading issues in response serialization
    result = await db.execute(
        select(Claim)
        .where(Claim.id == new_claim.id)
        .options(selectinload(Claim.expenses))
    )
    new_claim = result.scalar_one()

    from app.core.events import notify_n8n

    await notify_n8n(
        "CLAIM_OPENED",
        {
            "claim_id": str(new_claim.id),
            "policy_id": str(new_claim.policy_id),
            "client_id": str(new_claim.policy_id),  # Reference for n8n lookup
            "claim_type": new_claim.claim_type,
            "description": new_claim.description,
        },
    )

    # Pub/Sub event for creation
    await redis_client.publish(
        "claims_events",
        json.dumps(
            {
                "event": "CLAIM_REPORTED",
                "claim_id": str(new_claim.id),
                "policy_id": str(new_claim.policy_id),
            }
        ),
    )

    return new_claim


@audited(action="UPDATE_CLAIM_STATUS", entity="Claim")
async def update_claim_status(
    db: AsyncSession,
    claim_id: uuid.UUID,
    status_update: ClaimUpdateStatus,
    user_id: uuid.UUID,
) -> Claim:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )

    if not can_transition(claim.status, status_update.status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {claim.status} to {status_update.status}",
        )

    old_status = claim.status
    claim.status = status_update.status
    if claim.status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED]:
        claim.resolved_at = datetime.utcnow()

    await db.commit()

    result = await db.execute(
        select(Claim).where(Claim.id == claim.id).options(selectinload(Claim.expenses))
    )
    claim = result.scalar_one()

    # Emit event for other modules (like emission to set deceased_flag)
    if claim.status == ClaimStatus.APPROVED:
        from arq import create_pool
        from arq.connections import RedisSettings
        from app.core.config import settings
        from urllib.parse import urlparse

        u = urlparse(settings.REDIS_URL)
        redis_settings = RedisSettings(
            host=u.hostname, port=u.port, password=u.password
        )
        arq_redis = await create_pool(redis_settings)
        await arq_redis.enqueue_job(
            "process_approved_claim", str(claim.id), str(claim.beneficiary_id)
        )

    from app.core.events import notify_n8n

    await notify_n8n(
        "CLAIM_STATUS_CHANGED",
        {
            "claim_id": str(claim.id),
            "old_status": str(old_status),
            "new_status": str(claim.status),
            "assigned_to": str(user_id),
        },
    )

    return claim


@audited(action="ADD_CLAIM_EXPENSE", entity="ClaimExpense")
async def add_claim_expense(
    db: AsyncSession,
    claim_id: uuid.UUID,
    expense_in: ClaimExpenseCreate,
    user_id: uuid.UUID,
) -> ClaimExpense:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )

    expense = ClaimExpense(**expense_in.model_dump(), claim_id=claim.id)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def get_claim(db: AsyncSession, claim_id: uuid.UUID) -> Claim:
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id).options(selectinload(Claim.expenses))
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found"
        )
    return claim
