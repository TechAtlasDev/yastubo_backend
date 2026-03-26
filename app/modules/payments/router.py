import uuid
import stripe
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.payments.schemas import (
    CreatePaymentIntentRequest, CreateSubscriptionRequest, ManualPaymentRequest, 
    CancelSubscriptionRequest, TransactionResponse, SubscriptionResponse, 
    ConnectOnboardingResponse
)
from app.modules.payments import service, webhook_handler
from app.modules.payments.stripe_client import get_stripe_client, StripeClient

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/intent", response_model=TransactionResponse)
async def create_payment_intent(
    data: CreatePaymentIntentRequest,
    db: AsyncSession = Depends(get_db),
    stripe_c: StripeClient = Depends(get_stripe_client),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.create_one_time_payment(db, stripe_c, data, current_user.id)

@router.post("/subscription", response_model=SubscriptionResponse)
async def create_subscription(
    data: CreateSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    stripe_c: StripeClient = Depends(get_stripe_client),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.create_subscription(db, stripe_c, data, current_user.id)

@router.post("/subscription/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    data: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    stripe_c: StripeClient = Depends(get_stripe_client),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.cancel_subscription(db, stripe_c, data, admin_user.id)

@router.post("/manual", response_model=TransactionResponse)
async def register_manual_payment(
    data: ManualPaymentRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.register_manual_payment(db, data, admin_user.id)

@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    policy_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.list_transactions(db, policy_id=policy_id, status=status)

@router.post("/connect/onboarding", response_model=ConnectOnboardingResponse)
async def create_connect_onboarding(
    db: AsyncSession = Depends(get_db),
    stripe_c: StripeClient = Depends(get_stripe_client),
    current_user: User = Depends(get_current_user)
):
    return await service.create_connect_onboarding(db, stripe_c, current_user)

@router.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, stripe_c: StripeClient = Depends(get_stripe_client)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
    try:
        event = await stripe_c.construct_webhook_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process in background
    async def process_event():
        async with SessionLocal() as db:
            try:
                await webhook_handler.handle_stripe_event(event, db)
            except Exception as e:
                logger.error(f"Error processing Stripe webhook: {e}")

    background_tasks.add_task(process_event)
    
    return {"status": "success"}
