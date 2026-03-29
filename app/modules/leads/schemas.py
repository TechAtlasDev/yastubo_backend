import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.modules.leads.models import LeadStatus, FunnelStage


class LeadBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_e164: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")

    @field_validator("phone_e164", mode="before")
    @classmethod
    def normalize_e164(cls, v: str) -> str:
        if isinstance(v, str):
            stripped = v.strip()
            if stripped and not stripped.startswith("+"):
                stripped = "+" + stripped
            return stripped
        return v
    phone_raw: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: str = "es"
    country_of_residence: Optional[str] = Field(None, min_length=2, max_length=2)
    nationality: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = None
    state_region: Optional[str] = None


class LeadCreate(LeadBase):
    workspace_id: Optional[uuid.UUID] = None
    # Attribution fields
    source_channel: Optional[str] = None
    campaign_name: Optional[str] = None
    campaign_id: Optional[str] = None
    adset_id: Optional[str] = None
    ad_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    landing_page: Optional[str] = None
    referral_source: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    lead_status: Optional[LeadStatus] = None
    funnel_stage: Optional[FunnelStage] = None
    lead_score: Optional[int] = None
    intent_level: Optional[str] = None

    # Checkout tracking updates
    form_started: Optional[bool] = None
    form_completed: Optional[bool] = None
    checkout_started: Optional[bool] = None
    checkout_completed: Optional[bool] = None
    abandoned_checkout_flag: Optional[bool] = None
    purchase_completed: Optional[bool] = None


class LeadResponse(LeadBase):
    id: uuid.UUID
    lead_status: LeadStatus
    funnel_stage: FunnelStage
    lead_score: int
    created_at: datetime
    updated_at: datetime

    # Sync status
    zoho_lead_id: Optional[str] = None
    converted_to_contact_flag: bool

    model_config = ConfigDict(from_attributes=True)
