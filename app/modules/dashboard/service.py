import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.modules.payments.models import Transaction, Subscription
from app.modules.emission.models import Policy
from app.modules.leads.models import Lead
from app.modules.dashboard.schemas import DashboardKPIMetrics


async def get_dashboard_metrics(
    db: AsyncSession, workspace_id: uuid.UUID
) -> DashboardKPIMetrics:
    # 1. Total Revenue
    revenue_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.workspace_id == workspace_id, Transaction.status == "SUCCEEDED"
        )
    )
    revenue_res = await db.execute(revenue_stmt)
    total_revenue = Decimal(str(revenue_res.scalar() or 0))

    # 2. MRR (Monthly Recurring Revenue)
    mrr_stmt = select(func.sum(Subscription.monthly_price)).where(
        and_(Subscription.workspace_id == workspace_id, Subscription.status == "ACTIVE")
    )
    mrr_res = await db.execute(mrr_stmt)
    mrr = Decimal(str(mrr_res.scalar() or 0))

    # 3. Policy counts
    active_policies_stmt = select(func.count(Policy.id)).where(
        and_(Policy.workspace_id == workspace_id, Policy.status == "ACTIVE")
    )
    active_res = await db.execute(active_policies_stmt)
    active_policies = active_res.scalar() or 0

    pending_policies_stmt = select(func.count(Policy.id)).where(
        and_(Policy.workspace_id == workspace_id, Policy.status == "PENDING_PAYMENT")
    )
    pending_res = await db.execute(pending_policies_stmt)
    pending_policies = pending_res.scalar() or 0

    # 4. Churn Rate (last 30 days)
    last_30_days = datetime.now() - timedelta(days=30)
    cancelled_stmt = select(func.count(Policy.id)).where(
        and_(
            Policy.workspace_id == workspace_id,
            Policy.status == "CANCELLED",
            Policy.cancelled_at >= last_30_days,
        )
    )
    cancelled_res = await db.execute(cancelled_stmt)
    cancelled_count = cancelled_res.scalar() or 0
    churn_rate = (
        (cancelled_count / active_policies * 100) if active_policies > 0 else 0.0
    )

    # 5. LTV Average
    clients_stmt = select(func.count(func.distinct(Policy.client_id))).where(
        Policy.workspace_id == workspace_id
    )
    clients_res = await db.execute(clients_stmt)
    total_clients = clients_res.scalar() or 0
    ltv_average = (total_revenue / total_clients) if total_clients > 0 else Decimal(0)

    # 6. CAC Average (Mock for now, as we don't have ad spend in DB)
    # Recommended: Assume $15 USD CAC as default baseline for the machine
    cac_average = Decimal("15.00")

    # 7. Conversions by channel
    channels_stmt = (
        select(Lead.source_channel, func.count(Lead.id))
        .where(and_(Lead.workspace_id == workspace_id, Lead.purchase_completed))
        .group_by(Lead.source_channel)
    )
    channels_res = await db.execute(channels_stmt)
    conversions_by_channel = {row[0] or "Direct": row[1] for row in channels_res}

    # 8. Top Plans
    top_plans_stmt = (
        select(Policy.plan_version_snapshot["name"], func.count(Policy.id))
        .where(Policy.workspace_id == workspace_id)
        .group_by(Policy.plan_version_snapshot["name"])
        .order_by(func.count(Policy.id).desc())
        .limit(5)
    )
    top_plans_res = await db.execute(top_plans_stmt)
    top_plans = [{"name": row[0], "count": row[1]} for row in top_plans_res]

    return DashboardKPIMetrics(
        total_revenue=total_revenue,
        mrr=mrr,
        active_policies=active_policies,
        pending_payment_policies=pending_policies,
        churn_rate=churn_rate,
        cac_average=cac_average,
        ltv_average=ltv_average,
        conversions_by_channel=conversions_by_channel,
        revenue_by_month={},  # Placeholder for grouping
        top_plans=top_plans,
    )
