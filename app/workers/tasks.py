from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.modules.emission.models import Policy
from app.modules.emission.state_machine import PolicyStatus
from app.modules.payments.models import Transaction, Subscription
from app.modules.payments.stripe_client import StripeClient
from app.modules.notifications.service import get_notifications_service
from app.modules.audit import service as audit_service
from app.core.config import settings

async def send_payment_reminders(ctx):
    """Daily task to remind clients in arrears about their payments."""
    async with SessionLocal() as db:
        notifications = get_notifications_service()
        # 1. Get policies IN_ARREARS
        result = await db.execute(
            select(Policy)
            .where(Policy.status == PolicyStatus.IN_ARREARS)
            .options(selectinload(Policy.client))
        )
        policies = result.scalars().all()
        
        for policy in policies:
            # 2. Check for active subscription
            sub_res = await db.execute(
                select(Subscription)
                .where(Subscription.policy_id == policy.id, Subscription.status == "ACTIVE")
            )
            subscription = sub_res.scalar_one_or_none()
            
            if not subscription:
                # 3. No sub, send reminder
                await notifications.on_payment_reminder(policy, policy.client)
                
                # 4. Audit
                await audit_service.log(
                    db=db,
                    action="PAYMENT_REMINDER_SENT",
                    entity="Policy",
                    entity_id=policy.id,
                    extra={"policy_number": policy.policy_number}
                )
        
        await db.commit()

async def retry_failed_payments(ctx):
    """Task to retry failed transactions with attempt_count < 2."""
    stripe_client = ctx.get("stripe_client") or StripeClient(settings.STRIPE_SECRET_KEY)
    
    async with SessionLocal() as db:
        # 1. Get failed transactions
        result = await db.execute(
            select(Transaction)
            .where(
                Transaction.status == "FAILED",
                Transaction.attempt_count < 2,
                Transaction.stripe_payment_intent_id.is_not(None)
            )
            .options(selectinload(Transaction.policy))
        )
        transactions = result.scalars().all()
        
        for tx in transactions:
            try:
                # 2. Attempt confirm with Stripe
                pi = await stripe_client.confirm_payment_intent(
                    tx.stripe_payment_intent_id,
                    payment_method_id=None,
                )
                
                if pi["status"] == "succeeded":
                    tx.status = "SUCCEEDED"
                    tx.processed_at = datetime.now()
                    
                    # Update policy if needed
                    from app.modules.payments.service import on_payment_succeeded
                    await on_payment_succeeded(db=db, transaction=tx)
                else:
                    tx.attempt_count += 1
                    tx.last_error = f"Retry status: {pi['status']}"
                    
            except Exception as e:
                tx.attempt_count += 1
                tx.last_error = f"Retry error: {str(e)}"
        
        await db.commit()
