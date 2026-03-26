from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Numeric, Text, JSON, Date, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID

if TYPE_CHECKING:
    from app.modules.payments.models import Transaction

class Client(BaseModel):
    __tablename__ = "clients"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    nationality: Mapped[str] = mapped_column(String(2), nullable=False)
    country_of_residence: Mapped[str] = mapped_column(String(2), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Marketing & Attribution
    acquisition_channel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    campaign_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Retention & Risk
    churn_risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # LOW, MEDIUM, HIGH, CRITICAL
    collections_risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_failed_payment_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retention_sequence_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    winback_eligible_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Sync & External
    chatwoot_contact_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zoho_contact_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="client")

class Policy(BaseModel):
    __tablename__ = "policies"

    policy_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("plans.id"), nullable=False)
    plan_version_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT") # DRAFT, ACTIVE, PAST_DUE, CANCELLED
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    surcharge_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False) # Total of all beneficiaries
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issued_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="policies")
    beneficiaries: Mapped[List["Beneficiary"]] = relationship("Beneficiary", back_populates="policy", cascade="all, delete-orphan")
    status_history: Mapped[List["PolicyStatusHistory"]] = relationship("PolicyStatusHistory", back_populates="policy", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="policy")

class Beneficiary(BaseModel):
    __tablename__ = "beneficiaries"

    policy_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    kinship_type: Mapped[str] = mapped_column(String(50), nullable=False) # SELF, SPOUSE, CHILD, PARENT, OTHER
    country_of_residence: Mapped[str] = mapped_column(String(2), nullable=False)
    location_type: Mapped[str] = mapped_column(String(50), default="URBAN") # URBAN, RURAL

    # Status & Pricing
    coverage_status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    individual_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Critical Exception Handling
    deceased_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    deceased_reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deceased_reported_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backend_api_call_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    backend_api_call_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    billing_adjustment_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Sync
    zoho_beneficiary_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    snapshot_last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    policy: Mapped["Policy"] = relationship("Policy", back_populates="beneficiaries")

class PolicyStatusHistory(BaseModel):
    __tablename__ = "policy_status_history"

    policy_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    policy: Mapped["Policy"] = relationship("Policy", back_populates="status_history")
