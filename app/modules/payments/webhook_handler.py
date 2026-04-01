from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.modules.payments.models import Transaction, Subscription, StripeEvent
from app.modules.payments import service
from app.modules.emission.models import Policy
from app.modules.emission.state_machine import PolicyStatus
from app.modules.audit.models import AuditLog
from app.modules.notifications.service import get_notifications_service


async def handle_stripe_event(event: dict, db: AsyncSession) -> None:
    event_id = event.get("id")
    event_type = event.get("type")
    data_obj = event.get("data", {}).get("object", {})

    # 1. Idempotency Check
    res = await db.execute(select(StripeEvent).where(StripeEvent.event_id == event_id))
    if res.scalar_one_or_none():
        logger.info(f"Stripe event {event_id} already processed. Skipping.")
        return

    logger.info(f"Handling Stripe event: {event_type} ({event_id})")

    if event_type == "payment_intent.succeeded":
        pi_id = data_obj.get("id")
        res = await db.execute(
            select(Transaction)
            .where(Transaction.stripe_payment_intent_id == pi_id)
            .options(selectinload(Transaction.policy))
        )
        transaction = res.scalar_one_or_none()
        if transaction:
            transaction.status = "SUCCEEDED"
            transaction.processed_at = datetime.now()
            await service.on_payment_succeeded(db, transaction)

            # PHASE 2: Convert Lead if exists
            if transaction.policy and transaction.policy.lead_id:
                from app.modules.leads import service as leads_service
                from app.modules.leads.schemas import LeadUpdate

                await leads_service.update_lead(
                    db, transaction.policy.lead_id, LeadUpdate(purchase_completed=True)
                )
                logger.info(
                    f"Lead {transaction.policy.lead_id} converted to customer due to successful payment."
                )

            policy_res = await db.execute(
                select(Policy)
                .where(Policy.id == transaction.policy_id)
                .options(selectinload(Policy.client))
            )
            policy = policy_res.scalar_one_or_none()
            if policy and policy.client:
                notifications = get_notifications_service()
                await notifications.on_payment_confirmed(
                    policy, policy.client, transaction
                )

            # Record event as processed
            db.add(StripeEvent(event_id=event_id, event_type=event_type))
            await db.commit()

    elif event_type == "payment_intent.payment_failed":
        pi_id = data_obj.get("id")
        res = await db.execute(
            select(Transaction)
            .where(Transaction.stripe_payment_intent_id == pi_id)
            .options(selectinload(Transaction.policy))
        )
        transaction = res.scalar_one_or_none()
        if transaction:
            transaction.status = "FAILED"
            transaction.last_error = data_obj.get("last_payment_error", {}).get(
                "message"
            )
            transaction.attempt_count += 1

            policy_res = await db.execute(
                select(Policy)
                .where(Policy.id == transaction.policy_id)
                .options(selectinload(Policy.client))
            )
            policy = policy_res.scalar_one_or_none()
            if policy and policy.client:
                notifications = get_notifications_service()
                await notifications.on_payment_failed(
                    policy, policy.client, transaction.attempt_count
                )

                from app.core.events import notify_n8n

                await notify_n8n(
                    "PAYMENT_FAILED",
                    {
                        "transaction_id": str(transaction.id),
                        "policy_id": str(transaction.policy_id),
                        "amount": float(transaction.amount),
                        "error": transaction.last_error,
                        "attempt": transaction.attempt_count,
                    },
                )

                if transaction.attempt_count >= 2:
                    # Transition to IN_ARREARS
                    from app.modules.emission.service import change_policy_status
                    from app.modules.emission.schemas import StatusTransitionRequest

                    await change_policy_status(
                        db,
                        transaction.policy_id,
                        StatusTransitionRequest(
                            target_status=PolicyStatus.IN_ARREARS,
                            reason="Payment failed multiple times",
                        ),
                        transaction.policy.issued_by,
                    )
                    audit = AuditLog(
                        company_id=transaction.company_id,
                        action="PAYMENT_FAILED_MAX_RETRIES",
                        entity="Transaction",
                        user_id=None,
                        details=f"Payment failed max retries for {pi_id}",
                    )
                    db.add(audit)

            audit = AuditLog(
                company_id=transaction.company_id,
                action="PAYMENT_FAILED",
                entity="Transaction",
                user_id=None,
                details=f"Payment failed for {pi_id}",
            )
            db.add(audit)

            # Record event as processed
            db.add(StripeEvent(event_id=event_id, event_type=event_type))
            await db.commit()

    elif event_type == "customer.subscription.updated":
        sub_id = data_obj.get("id")
        res = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
        )
        subscription = res.scalar_one_or_none()
        if subscription:
            subscription.status = data_obj.get("status").upper()
            subscription.current_period_start = datetime.fromtimestamp(
                data_obj.get("current_period_start")
            )
            subscription.current_period_end = datetime.fromtimestamp(
                data_obj.get("current_period_end")
            )

            # Record event as processed
            db.add(StripeEvent(event_id=event_id, event_type=event_type))
            await db.commit()

    elif event_type == "customer.subscription.deleted":
        sub_id = data_obj.get("id")
        res = await db.execute(
            select(Subscription)
            .where(Subscription.stripe_subscription_id == sub_id)
            .options(selectinload(Subscription.policy))
        )
        subscription = res.scalar_one_or_none()
        if subscription:
            subscription.status = "CANCELLED"
            subscription.cancelled_at = datetime.now()

            # Transition Policy to CANCELLED
            from app.modules.emission.service import change_policy_status
            from app.modules.emission.schemas import StatusTransitionRequest

            await change_policy_status(
                db,
                subscription.policy_id,
                StatusTransitionRequest(
                    target_status=PolicyStatus.CANCELLED,
                    reason="Subscription deleted in Stripe",
                ),
                subscription.policy.issued_by,
            )
            audit = AuditLog(
                company_id=subscription.company_id,
                action="SUBSCRIPTION_CANCELLED",
                entity="Policy",
                user_id=None,
                details=f"Subscription deleted for {sub_id}",
            )
            db.add(audit)

            # Record event as processed
            db.add(StripeEvent(event_id=event_id, event_type=event_type))
            await db.commit()

    elif event_type == "invoice.payment_succeeded":
        sub_id = data_obj.get("subscription")
        if sub_id:
            res = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == sub_id
                )
            )
            subscription = res.scalar_one_or_none()
            if subscription:
                transaction = Transaction(
                    policy_id=subscription.policy_id,
                    stripe_payment_intent_id=data_obj.get("payment_intent"),
                    stripe_invoice_id=data_obj.get("id"),
                    amount=float(data_obj.get("amount_paid") / 100),
                    currency=data_obj.get("currency").upper(),
                    status="SUCCEEDED",
                    payment_type="SUBSCRIPTION_CHARGE",
                    processed_at=datetime.now(),
                )
                db.add(transaction)

                from app.core.events import notify_n8n

                await notify_n8n(
                    "SUBSCRIPTION_ACTIVATED",
                    {
                        "subscription_id": str(subscription.id),
                        "client_id": str(subscription.policy.client_id),
                        "plan_id": str(subscription.policy.plan_id),
                        "amount": float(transaction.amount),
                        "currency": transaction.currency,
                    },
                )

                audit = AuditLog(
                    company_id=subscription.company_id,
                    action="SUBSCRIPTION_PAYMENT_SUCCEEDED",
                    entity="Transaction",
                    user_id=None,
                    details=f"Subscription invoice paid for {sub_id}",
                )
                db.add(audit)

                # Record event as processed
                db.add(StripeEvent(event_id=event_id, event_type=event_type))
                await db.commit()
    else:
        logger.debug(f"Unhandled Stripe event type: {event_type}")
