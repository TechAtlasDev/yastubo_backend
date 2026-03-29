from pydantic import BaseModel
from typing import Dict, List
from decimal import Decimal


class DashboardKPIMetrics(BaseModel):
    total_revenue: Decimal
    mrr: Decimal
    active_policies: int
    pending_payment_policies: int
    churn_rate: float
    cac_average: Decimal
    ltv_average: Decimal
    loss_ratio: float
    total_claims_amount: Decimal
    active_beneficiaries: int
    conversions_by_channel: Dict[str, int]
    revenue_by_month: Dict[str, Decimal]
    top_plans: List[Dict[str, str | int]]
