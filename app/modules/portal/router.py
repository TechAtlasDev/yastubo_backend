import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.emission.models import Client
from app.modules.emission.schemas import PolicyResponse
from app.modules.payments.models import PaymentMethod
from app.modules.payments.stripe_client import get_stripe_client, StripeClient
from app.modules.portal import service as portal_service

router = APIRouter(prefix="/portal", tags=["Portal"])


async def get_client_for_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Client:
    # Logic: email matches
    return await portal_service.get_client_by_user_email(db, current_user.email)


@router.get("/me")
async def get_portal_me(client: Client = Depends(get_client_for_user)):
    return client


@router.get("/policies", response_model=List[PolicyResponse])
async def get_portal_policies(
    db: AsyncSession = Depends(get_db), client: Client = Depends(get_client_for_user)
):
    return await portal_service.get_client_policies(db, client.id)


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_portal_policy_detail(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    client: Client = Depends(get_client_for_user),
):
    return await portal_service.get_client_policy_detail(db, policy_id, client.id)


@router.get("/policies/{policy_id}/transactions")
async def get_portal_policy_transactions(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    client: Client = Depends(get_client_for_user),
):
    policy = await portal_service.get_client_policy_detail(db, policy_id, client.id)
    return policy.transactions


@router.post("/policies/{policy_id}/cancel")
async def cancel_portal_policy(
    policy_id: uuid.UUID,
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    client: Client = Depends(get_client_for_user),
):
    return await portal_service.cancel_policy_by_client(
        db, policy_id, client.id, reason
    )


@router.get("/payment-methods")
async def get_portal_payment_methods(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select

    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/payment-methods")
async def add_portal_payment_method(
    stripe_payment_method_id: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    stripe: StripeClient = Depends(get_stripe_client),
):
    return await portal_service.add_payment_method(
        db, stripe, current_user.id, stripe_payment_method_id
    )


@router.delete("/payment-methods/{pm_id}")
async def delete_portal_payment_method(
    pm_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(PaymentMethod).where(
            PaymentMethod.id == pm_id, PaymentMethod.user_id == current_user.id
        )
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Payment method not found")

    await db.delete(pm)
    await db.commit()
    return {"status": "deleted"}


@router.put("/payment-methods/{pm_id}/default")
async def set_default_portal_payment_method(
    pm_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select, update

    # Reset others
    await db.execute(
        update(PaymentMethod)
        .where(PaymentMethod.user_id == current_user.id)
        .values(is_default=False)
    )
    # Set this one
    result = await db.execute(
        select(PaymentMethod).where(
            PaymentMethod.id == pm_id, PaymentMethod.user_id == current_user.id
        )
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Payment method not found")

    pm.is_default = True
    await db.commit()
    return pm


@router.post("/policies/{policy_id}/pay")
async def pay_portal_policy(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    client: Client = Depends(get_client_for_user),
    stripe: StripeClient = Depends(get_stripe_client),
):
    return await portal_service.pay_pending_policy(db, stripe, policy_id, client.id)
