import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import BaseModel, GUID
import enum


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    LOST = "LOST"
    CONVERTED = "CONVERTED"


class FunnelStage(str, enum.Enum):
    AWARENESS = "AWARENESS"
    INTEREST = "INTEREST"
    CONSIDERATION = "CONSIDERATION"
    INTENT = "INTENT"
    PURCHASE = "PURCHASE"


class Lead(BaseModel):
    __tablename__ = "leads"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Identity
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_e164: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    phone_raw: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="es")
    country_of_residence: Mapped[Optional[str]] = mapped_column(
        String(2), nullable=True
    )
    nationality: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state_region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Attribution
    source_channel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    campaign_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    adset_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ad_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    landing_page: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referral_source: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Commercial
    lead_status: Mapped[LeadStatus] = mapped_column(String(50), default=LeadStatus.NEW)
    funnel_stage: Mapped[FunnelStage] = mapped_column(
        String(50), default=FunnelStage.AWARENESS
    )
    lead_score: Mapped[int] = mapped_column(Integer, default=0)
    intent_level: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # LOW, MEDIUM, HIGH

    # Conversation tracking
    first_contact_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_conversation_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_conversation_channel: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    conversation_status: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    whatsapp_opt_in_status: Mapped[bool] = mapped_column(Boolean, default=False)
    chatwoot_contact_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    chatwoot_conversation_id_last: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    assigned_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_handled_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    human_handoff_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    last_message_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Checkout tracking
    form_started: Mapped[bool] = mapped_column(Boolean, default=False)
    form_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    checkout_started: Mapped[bool] = mapped_column(Boolean, default=False)
    checkout_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    checkout_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    abandoned_checkout_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    abandoned_checkout_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    purchase_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Follow-up
    followup_whatsapp_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_whatsapp_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    followup_sequence_step: Mapped[int] = mapped_column(Integer, default=0)
    next_followup_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    converted_to_contact_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    backend_customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), nullable=True
    )  # Link to Client once converted

    # Sync
    zoho_lead_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    snapshot_last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
