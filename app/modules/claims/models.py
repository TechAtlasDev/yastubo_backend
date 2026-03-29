from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID

if TYPE_CHECKING:
    from app.modules.emission.models import Policy, Beneficiary
    from app.modules.workspaces.models import Workspace


class Claim(BaseModel):
    __tablename__ = "claims"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False
    )
    beneficiary_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="REPORTED"
    )  # REPORTED, IN_REVIEW, APPROVED, REJECTED, PAID
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    policy: Mapped["Policy"] = relationship("Policy", foreign_keys=[policy_id])
    beneficiary: Mapped["Beneficiary"] = relationship(
        "Beneficiary", foreign_keys=[beneficiary_id]
    )
    expenses: Mapped[List["ClaimExpense"]] = relationship(
        "ClaimExpense", back_populates="claim", cascade="all, delete-orphan"
    )
    commission_distributions: Mapped[List["CommissionDistribution"]] = relationship(
        "CommissionDistribution", back_populates="claim", cascade="all, delete-orphan"
    )


class ClaimExpense(BaseModel):
    __tablename__ = "claim_expenses"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    expense_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g. FUNERAL, LEGAL, MEDICAL
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    claim: Mapped["Claim"] = relationship("Claim", back_populates="expenses")


class CommissionDistribution(BaseModel):
    __tablename__ = "commission_distributions"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    claim: Mapped["Claim"] = relationship(
        "Claim", back_populates="commission_distributions"
    )
    workspace: Mapped["Workspace"] = relationship("Workspace")
