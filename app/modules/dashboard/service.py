import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.modules.payments.models import Transaction, Subscription
from app.modules.emission.models import Policy, Beneficiary
from app.modules.leads.models import Lead
from app.modules.claims.models import Claim, ClaimExpense
from app.modules.dashboard.schemas import DashboardKPIMetrics


async def get_dashboard_metrics(
    db: AsyncSession, company_id: uuid.UUID
) -> DashboardKPIMetrics:
    # 1. Total Revenue
    revenue_stmt = select(func.sum(Transaction.amount)).where(
        and_(Transaction.company_id == company_id, Transaction.status == "SUCCEEDED")
    )
    revenue_res = await db.execute(revenue_stmt)
    total_revenue = Decimal(str(revenue_res.scalar() or 0))

    # 2. MRR (Monthly Recurring Revenue)
    mrr_stmt = select(func.sum(Subscription.monthly_price)).where(
        and_(Subscription.company_id == company_id, Subscription.status == "ACTIVE")
    )
    mrr_res = await db.execute(mrr_stmt)
    mrr = Decimal(str(mrr_res.scalar() or 0))

    # 3. Policy counts
    active_policies_stmt = select(func.count(Policy.id)).where(
        and_(Policy.company_id == company_id, Policy.status == "ACTIVE")
    )
    active_res = await db.execute(active_policies_stmt)
    active_policies = active_res.scalar() or 0

    pending_policies_stmt = select(func.count(Policy.id)).where(
        and_(Policy.company_id == company_id, Policy.status == "PENDING_PAYMENT")
    )
    pending_res = await db.execute(pending_policies_stmt)
    pending_policies = pending_res.scalar() or 0

    # 4. Churn Rate (last 30 days)
    last_30_days = datetime.now() - timedelta(days=30)
    cancelled_stmt = select(func.count(Policy.id)).where(
        and_(
            Policy.company_id == company_id,
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
        Policy.company_id == company_id
    )
    clients_res = await db.execute(clients_stmt)
    total_clients = clients_res.scalar() or 0
    ltv_average = (total_revenue / total_clients) if total_clients > 0 else Decimal(0)

    # 6. Claims & Loss Ratio
    claims_stmt = (
        select(func.sum(ClaimExpense.amount))
        .join(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .where(Policy.company_id == company_id)
    )
    claims_res = await db.execute(claims_stmt)
    total_claims_amount = Decimal(str(claims_res.scalar() or 0))
    loss_ratio = (
        (float(total_claims_amount / total_revenue) * 100) if total_revenue > 0 else 0.0
    )

    # 7. Active Beneficiaries
    beneficiaries_stmt = (
        select(func.count(Beneficiary.id))
        .join(Policy)
        .where(
            and_(
                Policy.company_id == company_id,
                Beneficiary.coverage_status == "ACTIVE",
            )
        )
    )
    beneficiaries_res = await db.execute(beneficiaries_stmt)
    active_beneficiaries = beneficiaries_res.scalar() or 0

    # 8. CAC Average — computed as total_revenue / total converted leads
    # Returns 0.00 when ad spend data is unavailable; connect ad spend source to improve.
    converted_leads_stmt = select(func.count(Lead.id)).where(
        and_(Lead.company_id == company_id, Lead.purchase_completed == True)  # noqa: E712
    )
    converted_res = await db.execute(converted_leads_stmt)
    converted_leads = converted_res.scalar() or 0
    cac_average = (
        (total_revenue / converted_leads) if converted_leads > 0 else Decimal("0.00")
    )

    # 9. Conversions by channel
    channels_stmt = (
        select(Lead.source_channel, func.count(Lead.id))
        .where(and_(Lead.company_id == company_id, Lead.purchase_completed))
        .group_by(Lead.source_channel)
    )
    channels_res = await db.execute(channels_stmt)
    conversions_by_channel = {row[0] or "Direct": row[1] for row in channels_res}

    # 10. Top Plans
    top_plans_stmt = (
        select(Policy.plan_version_snapshot["name"], func.count(Policy.id))
        .where(Policy.company_id == company_id)
        .group_by(Policy.plan_version_snapshot["name"])
        .order_by(func.count(Policy.id).desc())
        .limit(5)
    )
    top_plans_res = await db.execute(top_plans_stmt)
    top_plans = [{"name": row[0], "count": row[1]} for row in top_plans_res]

    # 11. Revenue by month (last 12 months)
    revenue_by_month_stmt = (
        select(
            extract("year", Transaction.processed_at).label("year"),
            extract("month", Transaction.processed_at).label("month"),
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            and_(
                Transaction.company_id == company_id,
                Transaction.status == "SUCCEEDED",
                Transaction.processed_at >= datetime.now() - timedelta(days=365),
            )
        )
        .group_by("year", "month")
        .order_by("year", "month")
    )
    revenue_by_month_res = await db.execute(revenue_by_month_stmt)
    revenue_by_month = {
        f"{int(row.year)}-{int(row.month):02d}": Decimal(str(row.total or 0))
        for row in revenue_by_month_res
    }

    return DashboardKPIMetrics(
        total_revenue=total_revenue,
        mrr=mrr,
        active_policies=active_policies,
        pending_payment_policies=pending_policies,
        churn_rate=churn_rate,
        cac_average=cac_average,
        ltv_average=ltv_average,
        loss_ratio=loss_ratio,
        total_claims_amount=total_claims_amount,
        active_beneficiaries=active_beneficiaries,
        conversions_by_channel=conversions_by_channel,
        revenue_by_month=revenue_by_month,
        top_plans=top_plans,
    )
