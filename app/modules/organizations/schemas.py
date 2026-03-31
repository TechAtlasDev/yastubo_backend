import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BusinessUnitBase(BaseModel):
    name: str
    type: str = Field(..., description="'office', 'agency'")
    status: str = "active"
    parent_id: Optional[uuid.UUID] = None
    branding_text_dark: Optional[str] = None
    branding_bg_light: Optional[str] = None
    branding_text_light: Optional[str] = None
    branding_bg_dark: Optional[str] = None
    branding_logo_file_id: Optional[int] = None


class BusinessUnitCreate(BusinessUnitBase):
    pass


class BusinessUnitResponse(BusinessUnitBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    name: str
    short_code: str = Field(..., min_length=2, max_length=20)
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    branding_text_dark: Optional[str] = None
    branding_bg_light: Optional[str] = None
    branding_text_light: Optional[str] = None
    branding_bg_dark: Optional[str] = None
    branding_logo_file_id: Optional[int] = None
    pdf_template_id: Optional[int] = None
    commission_beneficiary_user_id: Optional[uuid.UUID] = None
    stripe_connect_id: Optional[str] = None
    is_active: bool = True
    is_reseller: bool = False
    commission_rate: float = 0.00


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    business_units: List[BusinessUnitResponse] = []

    model_config = ConfigDict(from_attributes=True)
