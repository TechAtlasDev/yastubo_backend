from pydantic import BaseModel
from typing import Dict, List, Optional
from decimal import Decimal

class DashboardKPIMetrics(BaseModel):
    total_revenue: Decimal
    mrr: Decimal
    active_policies: int
    pending_payment_policies: int
    churn_rate: float
    cac_average: Decimal
    ltv_average: Decimal
    conversions_by_channel: Dict[str, int]
    revenue_by_month: Dict[str, Decimal]
    top_plans: List[Dict[str, str | int]]
