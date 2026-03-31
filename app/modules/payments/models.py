from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    Boolean,
    JSON,
    DateTime,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID

if TYPE_CHECKING:
    from app.modules.auth.models import User
    from app.modules.emission.models import Policy


class Transaction(BaseModel):
    __tablename__ = "transactions"

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False
    )
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PENDING, SUCCEEDED, FAILED, REFUNDED, CANCELLED
    payment_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ONE_TIME, SUBSCRIPTION_CHARGE, MANUAL
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stripe_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    policy: Mapped["Policy"] = relationship("Policy", back_populates="transactions")


class PaymentMethod(BaseModel):
    __tablename__ = "payment_methods"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    stripe_payment_method_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    card_brand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    card_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    card_exp_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    card_exp_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User")


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    stripe_subscription_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ACTIVE, PAST_DUE, CANCELLED, UNPAID, TRIALING

    # Financial Snapshot (for CRM)
    plan_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    plan_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    monthly_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    billing_frequency: Mapped[str] = mapped_column(String(50), default="MONTHLY")
    mrr_snapshot: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    # Tracking
    failed_payment_count: Mapped[int] = mapped_column(Integer, default=0)
    beneficiaries_count: Mapped[int] = mapped_column(Integer, default=1)

    # Dates
    current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    subscription_created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    subscription_activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    renewal_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    next_payment_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Cancellation
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Sync
    zoho_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    snapshot_last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    policy: Mapped["Policy"] = relationship("Policy")


class StripeAccount(BaseModel):
    __tablename__ = "stripe_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    stripe_account_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    account_type: Mapped[str] = mapped_column(String(50), default="express")
    charges_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    payout_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User")


class StripeEvent(BaseModel):
    __tablename__ = "stripe_events"

    event_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
