import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CoverageBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class CoverageCreate(CoverageBase):
    pass


class CoverageResponse(CoverageBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class PlanVersionAgeSurchargeBase(BaseModel):
    min_age: int
    max_age: int
    surcharge_percentage: Decimal


class PlanVersionAgeSurchargeResponse(PlanVersionAgeSurchargeBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class PlanVersionCountryBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    price_override: Optional[Decimal] = None
    is_available: bool = True

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()


class PlanVersionCountryResponse(PlanVersionCountryBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class PlanVersionCoverageBase(BaseModel):
    coverage_id: uuid.UUID
    value_int: Optional[int] = None
    value_decimal: Optional[Decimal] = None
    value_text: Optional[Dict[str, Any]] = None
    notes: Optional[Dict[str, Any]] = None
    is_included: bool = True


class PlanVersionCoverageCreate(PlanVersionCoverageBase):
    pass


class PlanVersionCoverageResponse(PlanVersionCoverageBase):
    id: uuid.UUID
    coverage: Optional[CoverageResponse] = None
    model_config = ConfigDict(from_attributes=True)


class PlanVersionRepatriationCountryBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()


class PlanVersionRepatriationCountryResponse(PlanVersionRepatriationCountryBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class PlanVersionBase(BaseModel):
    version_number: int = 1
    cost_price: Optional[Decimal] = None
    public_price: Optional[Decimal] = None
    currency: str = "USD"
    max_entry_age: Optional[int] = None
    max_renewal_age: Optional[int] = None
    wtime_suicide: Optional[int] = None
    wtime_preexisting: Optional[int] = None
    wtime_accident: Optional[int] = None
    terms_es: Optional[str] = None
    terms_en: Optional[str] = None
    is_active: bool = True


class PlanVersionCreate(PlanVersionBase):
    age_surcharges: List[PlanVersionAgeSurchargeBase] = []
    countries: List[PlanVersionCountryBase] = []
    coverages: List[PlanVersionCoverageCreate] = []
    repatriation_countries: List[PlanVersionRepatriationCountryBase] = []


class PlanVersionResponse(PlanVersionBase):
    id: uuid.UUID
    plan_id: uuid.UUID
    created_at: datetime
    age_surcharges: List[PlanVersionAgeSurchargeResponse] = []
    countries: List[PlanVersionCountryResponse] = []
    coverages: List[PlanVersionCoverageResponse] = []
    repatriation_countries: List[PlanVersionRepatriationCountryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class PlanCreate(PlanBase):
    company_id: Optional[uuid.UUID] = None
    versions: List[PlanVersionCreate] = []


class PlanResponse(PlanBase):
    id: uuid.UUID
    product_id: uuid.UUID
    company_id: Optional[uuid.UUID] = None
    versions: List[PlanVersionResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_type: str = "repatriation"
    is_active: bool = True


class ProductCreate(ProductBase):
    plans: List[PlanCreate] = []


class ProductResponse(ProductBase):
    id: uuid.UUID
    plans: List[PlanResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# For backward compatibility / pricing logic (Optional, to be refactored)
class PriceCalculationRequest(BaseModel):
    plan_version_id: uuid.UUID
    age: int = Field(..., ge=0, le=120)
    country_code: str = Field(..., min_length=2, max_length=2)
    quantity: int = Field(1, ge=1)

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()


class PriceCalculationResponse(BaseModel):
    plan_version_id: uuid.UUID
    plan_name: str
    base_price: Decimal
    country_override: Optional[Decimal]
    age_surcharge_percentage: Decimal
    age_surcharge_amount: Decimal
    final_price: Decimal
    currency: str
    breakdown: dict
