import uuid
from typing import Optional
from pydantic import BaseModel, Field


class CurrencyBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str
    symbol: Optional[str] = None
    is_active: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):
    id: int

    class Config:
        from_attributes = True


class UnitOfMeasureBase(BaseModel):
    name: dict
    description: Optional[str] = None
    measure_type: str
    status: str = "active"


class UnitOfMeasureCreate(UnitOfMeasureBase):
    pass


class UnitOfMeasureResponse(UnitOfMeasureBase):
    id: int

    class Config:
        from_attributes = True


class CommissionUserBase(BaseModel):
    user_id: uuid.UUID
    commission_percentage: float = Field(..., ge=0, le=100)


class CompanyCommissionUserCreate(CommissionUserBase):
    company_id: uuid.UUID


class CompanyCommissionUserResponse(CommissionUserBase):
    id: uuid.UUID
    company_id: uuid.UUID

    class Config:
        from_attributes = True


class BUCommissionUserCreate(CommissionUserBase):
    business_unit_id: uuid.UUID


class BUCommissionUserResponse(CommissionUserBase):
    id: uuid.UUID
    business_unit_id: uuid.UUID

    class Config:
        from_attributes = True


class CommissionDispersionRequest(BaseModel):
    amount: float
    company_id: uuid.UUID
    business_unit_id: Optional[uuid.UUID] = None


class CommissionSplit(BaseModel):
    user_id: uuid.UUID
    percentage: float
    amount: float
    level: str
