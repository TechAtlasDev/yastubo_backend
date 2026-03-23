import uuid
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.modules.emission.state_machine import PolicyStatus

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    birth_date: date
    nationality: str = Field(..., min_length=2, max_length=2)
    country_of_residence: str = Field(..., min_length=2, max_length=2)
    document_type: str
    document_number: str
    address: Optional[str] = None

    @field_validator("nationality", "country_of_residence")
    @classmethod
    def uppercase_codes(cls, v: str) -> str:
        return v.upper()

class ClientResponse(ClientCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EmissionRequest(BaseModel):
    client_id: uuid.UUID
    plan_id: uuid.UUID
    country_code: str = Field(..., min_length=2, max_length=2)
    start_date: date
    notes: Optional[str] = None

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("start_date cannot be in the past")
        return v

class StatusHistoryResponse(BaseModel):
    id: uuid.UUID
    from_status: Optional[str]
    to_status: str
    changed_by: uuid.UUID
    reason: Optional[str]
    changed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PolicyResponse(BaseModel):
    id: uuid.UUID
    policy_number: str
    client_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    base_price: Decimal
    surcharge_amount: Decimal
    final_price: Decimal
    currency: str
    country_code: str
    insured_age: int
    start_date: Optional[date]
    end_date: Optional[date]
    pdf_path: Optional[str]
    notes: Optional[str]
    issued_by: uuid.UUID
    issued_at: Optional[datetime]
    client: ClientResponse
    status_history: List[StatusHistoryResponse]
    model_config = ConfigDict(from_attributes=True)

class EmissionResponse(BaseModel):
    policy: PolicyResponse
    pdf_url: str
    message: str

class StatusTransitionRequest(BaseModel):
    target_status: PolicyStatus
    reason: Optional[str] = None
