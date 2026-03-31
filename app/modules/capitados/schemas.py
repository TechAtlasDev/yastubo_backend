from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class BatchSummary(BaseModel):
    total_rows: int
    total_applied: int
    total_rejected: int
    total_duplicated: int
    total_incongruences: int
    total_plan_errors: int

    model_config = ConfigDict(from_attributes=True)


class BatchLogRead(BaseModel):
    id: UUID
    company_id: UUID
    coverage_month: date
    status: str
    reconciliation_status: str
    processed_at: Optional[datetime] = None
    original_filename: Optional[str] = None
    total_rows: int
    total_applied: int
    total_rejected: int
    total_duplicated: int
    error_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BatchItemLogRead(BaseModel):
    id: UUID
    row_number: int
    document_number: Optional[str] = None
    full_name: Optional[str] = None
    result: str
    rejection_code: Optional[str] = None
    rejection_detail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
