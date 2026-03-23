import uuid
from datetime import datetime, timezone
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.payments.models import Transaction, Subscription, StripeAccount, PaymentMethod
from app.modules.payments.schemas import CreatePaymentIntentRequest, CreateSubscriptionRequest, ManualPaymentRequest, CancelSubscriptionRequest
from app.modules.payments.stripe_client import StripeClient
from app.modules.emission.models import Policy
from app.modules.emission import service as emission_service
from app.modules.emission.state_machine import PolicyStatus, transition
from app.modules.auth.models import User, Role
from app.modules.audit.decorator import audited
from app.modules.plans.models import Plan
from app.core.config import settings

async def get_or_create_customer(stripe: StripeClient, client_user: User) -> str:
    # In this MVP we check if metadata or a field has stripe_id
    # For now, we create a new one each time OR we assume one exists.
    customer = await stripe.create_customer(
        email=client_user.email,
        name=f"{client_user.first_name} {client_user.last_name}",
        metadata={"user_id": str(client_user.id)}
    )
    return customer["id"]

async def create_one_time_payment(db: AsyncSession, stripe: StripeClient, data: CreatePaymentIntentRequest, issued_by: uuid.UUID) -> Transaction:
    policy = await emission_service.get_policy(db, data.policy_id)
    if policy.status != PolicyStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=422, detail=f"Policy status must be PENDING_PAYMENT, currently {policy.status}")
    
    customer_id = await get_or_create_customer(stripe, policy.client)
    
    amount_cents = int(policy.final_price * 100)
    pi = await stripe.create_payment_intent(
        amount_cents=amount_cents,
        currency=policy.currency.lower(),
        customer_id=customer_id,
        payment_method_id=data.payment_method_id,
        metadata={
            "policy_id": str(policy.id),
            "policy_number": policy.policy_number,
            "client_email": policy.client.email
        }
    )
    
    transaction = Transaction(
        policy_id=policy.id,
        stripe_payment_intent_id=pi["id"],
        amount=float(policy.final_price),
        currency=policy.currency,
        status="PENDING",
        payment_type="ONE_TIME",
        stripe_metadata=pi.get("metadata")
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    transaction.client_secret = pi.get("client_secret")
    return transaction

@audited(action="PAYMENT_SUCCEEDED", entity="Transaction")
async def on_payment_succeeded(db: AsyncSession, transaction: Transaction):
    # Ensure transaction is in current session
    transaction = await db.merge(transaction)
    transaction.status = "SUCCEEDED"
    transaction.processed_at = datetime.now()
    
    policy = await emission_service.get_policy(db, transaction.policy_id)
    
    if policy.status == PolicyStatus.PENDING_PAYMENT:
        # Transition to ACTIVE
        from app.modules.emission.service import change_policy_status
        from app.modules.emission.schemas import StatusTransitionRequest
        await change_policy_status(
            db=db, 
            policy_id=policy.id, 
            data=StatusTransitionRequest(target_status=PolicyStatus.ACTIVE, reason="Payment succeeded"), 
            changed_by=policy.issued_by # or system user
        )
    
    await db.commit()

@audited(action="SUBSCRIPTION_CREATED", entity="Policy")
async def create_subscription(db: AsyncSession, stripe: StripeClient, data: CreateSubscriptionRequest, issued_by: uuid.UUID) -> Subscription:
    policy = await emission_service.get_policy(db, data.policy_id)
    
    # Check if existing active subscription
    existing = await db.execute(select(Subscription).where(Subscription.policy_id == policy.id, Subscription.status == "ACTIVE"))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Policy already has an active subscription")
    
    # Plan must have stripe_price_id
    plan_res = await db.execute(select(Plan).where(Plan.id == policy.plan_id))
    plan = plan_res.scalar_one()
    if not plan.stripe_price_id:
        raise HTTPException(status_code=422, detail="Plan is not configured for subscriptions (missing price_id)")

    customer_id = await get_or_create_customer(stripe, policy.client)
    
    stripe_sub = await stripe.create_subscription(
        customer_id=customer_id,
        price_id=plan.stripe_price_id,
        payment_method_id=data.stripe_payment_method_id,
        metadata={"policy_id": str(policy.id)}
    )
    
    sub = Subscription(
        policy_id=policy.id,
        stripe_subscription_id=stripe_sub["id"],
        stripe_customer_id=customer_id,
        status=stripe_sub["status"].upper(),
        current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"], tz=timezone.utc),
        current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"], tz=timezone.utc)
    )
    db.add(sub)
    
    # Create initial transaction
    pi_id = None
    if stripe_sub.get("latest_invoice") and stripe_sub["latest_invoice"].get("payment_intent"):
        pi_id = stripe_sub["latest_invoice"]["payment_intent"]["id"]

    transaction = Transaction(
        policy_id=policy.id,
        stripe_payment_intent_id=pi_id,
        stripe_invoice_id=stripe_sub.get("latest_invoice", {}).get("id"),
        amount=float(policy.final_price), # Should match subscription price
        currency=policy.currency,
        status="PENDING",
        payment_type="SUBSCRIPTION_CHARGE"
    )
    db.add(transaction)
    
    await db.commit()
    await db.refresh(sub)
    return sub

@audited(action="SUBSCRIPTION_CANCELLED_BY_ADMIN", entity="Subscription")
async def cancel_subscription(db: AsyncSession, stripe: StripeClient, data: CancelSubscriptionRequest, cancelled_by: uuid.UUID) -> Subscription:
    res = await db.execute(select(Subscription).where(Subscription.policy_id == data.policy_id))
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    stripe_sub = await stripe.cancel_subscription(sub.stripe_subscription_id, data.cancel_immediately == False)
    
    sub.status = stripe_sub["status"].upper()
    sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
    if stripe_sub["status"] == "canceled":
        sub.cancelled_at = datetime.now()
    
    await db.commit()
    await db.refresh(sub)
    return sub

@audited(action="MANUAL_PAYMENT_REGISTERED", entity="Policy")
async def register_manual_payment(db: AsyncSession, data: ManualPaymentRequest, registered_by: uuid.UUID) -> Transaction:
    policy = await emission_service.get_policy(db, data.policy_id)
    
    transaction = Transaction(
        policy_id=policy.id,
        amount=float(data.amount),
        currency=policy.currency,
        status="SUCCEEDED",
        payment_type="MANUAL",
        processed_at=datetime.now(),
        last_error=data.notes
    )
    db.add(transaction)
    await db.flush()
    
    await on_payment_succeeded(db=db, transaction=transaction)
    
    await db.commit()
    await db.refresh(transaction)
    return transaction

async def create_connect_onboarding(db: AsyncSession, stripe: StripeClient, user: User) -> dict:
    # Verify vendedor role
    if not any(r.name == "VENDEDOR" for r in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only VENDEDOR can create Stripe account")
    
    res = await db.execute(select(StripeAccount).where(StripeAccount.user_id == user.id))
    acc = res.scalar_one_or_none()
    
    if not acc:
        stripe_acc = await stripe.create_connect_account(email=user.email, metadata={"user_id": str(user.id)})
        acc = StripeAccount(
            user_id=user.id,
            stripe_account_id=stripe_acc["id"]
        )
        db.add(acc)
        await db.commit()
        await db.refresh(acc)
    
    link = await stripe.create_account_link(
        account_id=acc.stripe_account_id,
        refresh_url=f"{settings.FRONTEND_URL}/connect/refresh",
        return_url=f"{settings.FRONTEND_URL}/connect/return"
    )
    
    return {"url": link["url"], "account_id": acc.stripe_account_id}

async def list_transactions(db: AsyncSession, policy_id: Optional[uuid.UUID] = None, status: Optional[str] = None) -> List[Transaction]:
    query = select(Transaction).options(selectinload(Transaction.policy))
    if policy_id:
        query = query.where(Transaction.policy_id == policy_id)
    if status:
        query = query.where(Transaction.status == status)
    
    res = await db.execute(query)
    return list(res.scalars().all())
