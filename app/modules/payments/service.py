import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.payments.models import Transaction, Subscription, StripeAccount
from app.modules.organizations.models import Company
from app.modules.payments.schemas import (
    CreatePaymentIntentRequest,
    CreateSubscriptionRequest,
    ManualPaymentRequest,
    CancelSubscriptionRequest,
)
from app.modules.payments.stripe_client import StripeClient
from app.modules.emission import service as emission_service
from app.modules.emission.state_machine import PolicyStatus
from app.modules.auth.models import User
from app.modules.audit.decorator import audited
from app.core.config import settings


async def get_or_create_customer(stripe: StripeClient, client_user: User) -> str:
    existing_id = await stripe.get_customer_id_by_email(client_user.email)
    if existing_id:
        return existing_id
    customer = await stripe.create_customer(
        email=client_user.email,
        name=f"{client_user.first_name} {client_user.last_name}",
        metadata={"user_id": str(client_user.id)},
    )
    return customer["id"]


async def create_one_time_payment(
    db: AsyncSession,
    stripe: StripeClient,
    data: CreatePaymentIntentRequest,
    issued_by: uuid.UUID,
) -> Transaction:
    policy = await emission_service.get_policy(db, data.policy_id)
    if policy.status != PolicyStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=422,
            detail=f"Policy status must be PENDING_PAYMENT, currently {policy.status}",
        )

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
            "client_email": policy.client.email,
        },
    )

    ws_id = policy.company_id
    if not ws_id:
        res_ws = await db.execute(select(Company.id).limit(1))
        ws_id = res_ws.scalar_one_or_none() or uuid.UUID(
            "00000000-0000-0000-0000-000000000000"
        )  # Should not happen

    transaction = Transaction(
        company_id=ws_id,
        policy_id=policy.id,
        stripe_payment_intent_id=pi["id"],
        amount=float(policy.final_price),
        currency=policy.currency,
        status="PENDING",
        payment_type="ONE_TIME",
        stripe_metadata=pi.get("metadata"),
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
            data=StatusTransitionRequest(
                target_status=PolicyStatus.ACTIVE, reason="Payment succeeded"
            ),
            changed_by=policy.issued_by,  # or system user
        )

    await db.commit()


@audited(action="SUBSCRIPTION_CREATED", entity="Policy")
async def create_subscription(
    db: AsyncSession,
    stripe: StripeClient,
    data: CreateSubscriptionRequest,
    issued_by: uuid.UUID,
) -> Subscription:
    policy = await emission_service.get_policy(db, data.policy_id)

    # Get Company for commissions
    res_ws = await db.execute(select(Company).where(Company.id == policy.company_id))
    company = res_ws.scalar_one()

    connect_account_id = None
    app_fee_percent = None

    if company.is_reseller and company.stripe_connect_id:
        connect_account_id = company.stripe_connect_id
        if company.commission_rate > 0:
            app_fee_percent = float(company.commission_rate)

    # Check if existing active subscription
    existing = await db.execute(
        select(Subscription).where(
            Subscription.policy_id == policy.id, Subscription.status == "ACTIVE"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Policy already has an active subscription"
        )

    # Plan must have stripe_price_id (Legacy check removed, using placeholder)
    # In a future phase, this should come from PlanVersion
    stripe_price_id = "price_placeholder"

    customer_id = await get_or_create_customer(stripe, policy.client)

    stripe_sub = await stripe.create_subscription(
        customer_id=customer_id,
        price_id=stripe_price_id,
        payment_method_id=data.stripe_payment_method_id,
        metadata={
            "policy_id": str(policy.id),
            "company_id": str(policy.company_id),
        },
        connect_account_id=connect_account_id,
        application_fee_percent=app_fee_percent,
    )

    ws_id = policy.company_id
    if not ws_id:
        res_ws = await db.execute(select(Company.id).limit(1))
        ws_id = res_ws.scalar_one_or_none()

    sub = Subscription(
        company_id=ws_id,
        policy_id=policy.id,
        stripe_subscription_id=stripe_sub["id"],
        stripe_customer_id=customer_id,
        status=stripe_sub["status"].upper(),
        current_period_start=datetime.fromtimestamp(
            stripe_sub["current_period_start"], tz=timezone.utc
        ),
        current_period_end=datetime.fromtimestamp(
            stripe_sub["current_period_end"], tz=timezone.utc
        ),
    )
    db.add(sub)

    # Create initial transaction
    pi_id = None
    if stripe_sub.get("latest_invoice") and stripe_sub["latest_invoice"].get(
        "payment_intent"
    ):
        pi_id = stripe_sub["latest_invoice"]["payment_intent"]["id"]

    transaction = Transaction(
        company_id=ws_id,
        policy_id=policy.id,
        stripe_payment_intent_id=pi_id,
        stripe_invoice_id=stripe_sub.get("latest_invoice", {}).get("id"),
        amount=float(policy.final_price),  # Should match subscription price
        currency=policy.currency,
        status="PENDING",
        payment_type="SUBSCRIPTION_CHARGE",
    )
    db.add(transaction)

    await db.commit()
    await db.refresh(sub)
    return sub


@audited(action="SUBSCRIPTION_CANCELLED_BY_ADMIN", entity="Subscription")
async def cancel_subscription(
    db: AsyncSession,
    stripe: StripeClient,
    data: CancelSubscriptionRequest,
    cancelled_by: uuid.UUID,
) -> Subscription:
    res = await db.execute(
        select(Subscription).where(Subscription.policy_id == data.policy_id)
    )
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    stripe_sub = await stripe.cancel_subscription(
        sub.stripe_subscription_id, not data.cancel_immediately
    )

    sub.status = stripe_sub["status"].upper()
    sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
    if stripe_sub["status"] == "canceled":
        sub.cancelled_at = datetime.now()

    await db.commit()
    await db.refresh(sub)
    return sub


@audited(action="MANUAL_PAYMENT_REGISTERED", entity="Policy")
async def register_manual_payment(
    db: AsyncSession, data: ManualPaymentRequest, registered_by: uuid.UUID
) -> Transaction:
    policy = await emission_service.get_policy(db, data.policy_id)

    transaction = Transaction(
        company_id=policy.company_id,
        policy_id=policy.id,
        amount=float(data.amount),
        currency=policy.currency,
        status="SUCCEEDED",
        payment_type="MANUAL",
        processed_at=datetime.now(),
        last_error=data.notes,
    )
    db.add(transaction)
    await db.flush()

    await on_payment_succeeded(db=db, transaction=transaction)

    await db.commit()
    await db.refresh(transaction)
    return transaction


async def create_connect_onboarding(
    db: AsyncSession, stripe: StripeClient, user: User
) -> dict:
    # Verify vendedor role
    if not any(r.name == "VENDEDOR" for r in user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only VENDEDOR can create Stripe account",
        )

    res = await db.execute(
        select(StripeAccount).where(StripeAccount.user_id == user.id)
    )
    acc = res.scalar_one_or_none()

    if not acc:
        stripe_acc = await stripe.create_connect_account(
            email=user.email, metadata={"user_id": str(user.id)}
        )
        acc = StripeAccount(user_id=user.id, stripe_account_id=stripe_acc["id"])
        db.add(acc)
        await db.commit()
        await db.refresh(acc)

    link = await stripe.create_account_link(
        account_id=acc.stripe_account_id,
        refresh_url=f"{settings.FRONTEND_URL}/connect/refresh",
        return_url=f"{settings.FRONTEND_URL}/connect/return",
    )

    return {"url": link["url"], "account_id": acc.stripe_account_id}


async def get_connect_status(
    db: AsyncSession, stripe: StripeClient, user: User
) -> dict:
    res = await db.execute(
        select(StripeAccount).where(StripeAccount.user_id == user.id)
    )
    acc = res.scalar_one_or_none()

    if not acc:
        return {
            "is_verified": False,
            "onboarding_complete": False,
            "stripe_account_id": None,
            "charges_enabled": False,
            "payouts_enabled": False,
            "details_submitted": False,
        }

    # Fetch account details from Stripe
    stripe_acc = await stripe.get_connect_account(acc.stripe_account_id)

    # Update local record if changed
    acc.onboarding_complete = stripe_acc.get("details_submitted", False)
    acc.is_verified = stripe_acc.get("charges_enabled", False)
    await db.commit()

    return {
        "is_verified": stripe_acc.get("charges_enabled", False),
        "onboarding_complete": stripe_acc.get("details_submitted", False),
        "stripe_account_id": acc.stripe_account_id,
        "charges_enabled": stripe_acc.get("charges_enabled", False),
        "payouts_enabled": stripe_acc.get("payouts_enabled", False),
        "details_submitted": stripe_acc.get("details_submitted", False),
    }


async def get_reseller_dashboard(db: AsyncSession, company_id: uuid.UUID) -> dict:
    from sqlalchemy import func

    # Total sales (Succeeded transactions)
    query_sales = select(
        func.count(Transaction.id).label("count"),
        func.sum(Transaction.amount).label("total_amount"),
    ).where(Transaction.company_id == company_id, Transaction.status == "SUCCEEDED")
    res_sales = await db.execute(query_sales)
    sales_stats = res_sales.one()

    # Get Company to know commission rate
    res_ws = await db.execute(select(Company).where(Company.id == company_id))
    company = res_ws.scalar_one()

    # Calculate earned commissions (based on sales amount and company rate)
    total_amount = sales_stats.total_amount or 0.0
    # If commission_rate is what platform keeps, then reseller gets (100 - rate)%
    # Based on our previous assumption in create_payment_intent:
    # Reseller is the destination, Platform takes Application Fee (commission_rate).
    # So Reseller gets: total_amount - application_fee.
    platform_rate = float(company.commission_rate) / 100.0
    earned = float(total_amount) * (1.0 - platform_rate)

    # Fetch pending balance from Stripe Connect account
    pending_commissions = 0.0
    # Use company.stripe_connect_id if available
    stripe_account_id = company.stripe_connect_id

    if stripe_account_id:
        try:
            import stripe as stripe_lib
            from app.core.config import settings as _settings

            stripe_lib.api_key = _settings.STRIPE_SECRET_KEY
            import asyncio as _asyncio

            balance = await _asyncio.to_thread(
                stripe_lib.Balance.retrieve,
                stripe_account=stripe_account_id,
            )
            pending = balance.get("pending", [])
            pending_commissions = sum(
                p.get("amount", 0) / 100.0
                for p in pending
                if p.get("currency", "usd") == "usd"
            )
        except Exception as exc:
            from loguru import logger as _logger

            _logger.warning(
                "[RESELLER_DASHBOARD] Could not fetch Stripe balance: {}", exc
            )

    return {
        "total_sales_count": sales_stats.count,
        "total_sales_amount": total_amount,
        "total_commissions_earned": earned,
        "pending_commissions": pending_commissions,
        "currency": "USD",
    }


MAX_PAYMENT_ATTEMPTS = 2


@audited(action="PAYMENT_RETRY", entity="Transaction")
async def retry_payment(
    db: AsyncSession,
    stripe: StripeClient,
    transaction_id: uuid.UUID,
    retried_by: uuid.UUID,
) -> dict:
    """
    Reintenta un cobro fallido. Máximo 2 intentos.
    - Si attempt_count < MAX_PAYMENT_ATTEMPTS: crea un nuevo PaymentIntent.
    - Si attempt_count >= MAX_PAYMENT_ATTEMPTS: notifica al cliente para
      actualizar su método de pago y lanza excepción.
    """
    from app.modules.notifications.service import get_notifications_service

    res = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(selectinload(Transaction.policy))
    )
    transaction = res.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status != "FAILED":
        raise HTTPException(
            status_code=422,
            detail=f"Only FAILED transactions can be retried. Current status: {transaction.status}",
        )

    policy = await emission_service.get_policy(db, transaction.policy_id)
    client = policy.client

    # Limit reached: notify and block
    if transaction.attempt_count >= MAX_PAYMENT_ATTEMPTS:
        notifications = get_notifications_service()
        await notifications.on_payment_failed(policy, client, transaction.attempt_count)
        raise HTTPException(
            status_code=422,
            detail=(
                f"Maximum retry attempts ({MAX_PAYMENT_ATTEMPTS}) reached. "
                "A payment update notification has been sent to the client."
            ),
        )

    # Proceed with retry
    customer_id = await get_or_create_customer(stripe, client)
    amount_cents = int(float(transaction.amount) * 100)

    pi = await stripe.create_payment_intent(
        amount_cents=amount_cents,
        currency=transaction.currency.lower(),
        customer_id=customer_id,
        payment_method_id=None,
        metadata={
            "policy_id": str(policy.id),
            "policy_number": policy.policy_number,
            "retry_of": str(transaction.id),
            "attempt": str(transaction.attempt_count + 1),
        },
    )

    transaction.attempt_count += 1
    transaction.status = "PENDING"
    transaction.stripe_payment_intent_id = pi["id"]
    transaction.last_error = None
    await db.commit()
    await db.refresh(transaction)

    return {
        "transaction_id": transaction.id,
        "attempt_count": transaction.attempt_count,
        "status": transaction.status,
        "message": f"Retry attempt {transaction.attempt_count} of {MAX_PAYMENT_ATTEMPTS} initiated.",
        "client_secret": pi.get("client_secret"),
    }


async def list_transactions(
    db: AsyncSession,
    policy_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
) -> List[Transaction]:
    query = select(Transaction).options(selectinload(Transaction.policy))
    if policy_id:
        query = query.where(Transaction.policy_id == policy_id)
    if status:
        query = query.where(Transaction.status == status)

    res = await db.execute(query)
    return list(res.scalars().all())
