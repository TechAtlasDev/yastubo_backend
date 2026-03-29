from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class ClaimExpenseBase(BaseModel):
    amount: float
    currency: str = "USD"
    expense_type: str
    receipt_url: Optional[str] = None


class ClaimExpenseCreate(ClaimExpenseBase):
    pass


class ClaimExpenseResponse(ClaimExpenseBase):
    id: uuid.UUID
    claim_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class ClaimBase(BaseModel):
    policy_id: uuid.UUID
    beneficiary_id: uuid.UUID
    description: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdateStatus(BaseModel):
    status: str
    reason: Optional[str] = None


class ClaimResponse(ClaimBase):
    id: uuid.UUID
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    expenses: List[ClaimExpenseResponse] = []

    model_config = ConfigDict(from_attributes=True)
