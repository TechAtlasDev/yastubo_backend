import uuid
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class CoverageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    limit_amount: Optional[Decimal] = None
    limit_unit: Optional[str] = None
    notes_es: Optional[str] = None
    notes_en: Optional[str] = None

class CoverageResponse(CoverageCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class AgeRangeCreate(BaseModel):
    min_age: int
    max_age: int
    surcharge_percentage: Decimal

class CountryConfigCreate(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    base_price_override: Optional[Decimal] = None
    is_available: bool = True

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()

class PlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: Decimal
    currency: str = "USD"
    max_entry_age: int
    max_renewal_age: int
    repatriation_countries: List[str]
    terms_es: Optional[str] = None
    terms_en: Optional[str] = None
    age_ranges: List[AgeRangeCreate]
    country_configs: List[CountryConfigCreate]
    coverage_ids: List[uuid.UUID]

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    currency: Optional[str] = None
    max_entry_age: Optional[int] = None
    max_renewal_age: Optional[int] = None
    repatriation_countries: Optional[List[str]] = None
    terms_es: Optional[str] = None
    terms_en: Optional[str] = None
    age_ranges: Optional[List[AgeRangeCreate]] = None
    country_configs: Optional[List[CountryConfigCreate]] = None
    coverage_ids: Optional[List[uuid.UUID]] = None

class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: Optional[str]
    base_price: Decimal
    currency: str
    is_active: bool
    max_entry_age: int
    max_renewal_age: int
    repatriation_countries: List[str]
    terms_es: Optional[str]
    terms_en: Optional[str]
    coverages: List[CoverageResponse]
    age_ranges: List[AgeRangeCreate]
    country_configs: List[CountryConfigCreate]
    current_version: int = 1
    created_at: datetime

class PriceCalculationRequest(BaseModel):
    plan_id: uuid.UUID
    age: int = Field(..., ge=0, le=120)
    country_code: str = Field(..., min_length=2, max_length=2)
    quantity: int = Field(1, ge=1)

    @field_validator("country_code")
    @classmethod
    def uppercase_country_code(cls, v: str) -> str:
        return v.upper()

class PriceCalculationResponse(BaseModel):
    plan_id: uuid.UUID
    plan_name: str
    base_price: Decimal
    country_override: Optional[Decimal]
    age_surcharge_percentage: Decimal
    age_surcharge_amount: Decimal
    final_price: Decimal
    currency: str
    breakdown: dict
