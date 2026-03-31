import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.auth.models import User
from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    DateTime,
    func,
    Numeric,
    Text,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID
from app.core.database import Base


class Company(BaseModel):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)

    # Branding
    branding_text_dark: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    branding_bg_light: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    branding_text_light: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True
    )
    branding_bg_dark: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    branding_logo_file_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )

    # New from legacy
    pdf_template_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    commission_beneficiary_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # From current Company (formerly Workspace)
    stripe_connect_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_reseller: Mapped[bool] = mapped_column(Boolean, default=False)
    commission_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0.00, nullable=False
    )

    business_units: Mapped[List["BusinessUnit"]] = relationship(
        "BusinessUnit", back_populates="company"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="company_user", back_populates="companies"
    )


class BusinessUnit(BaseModel):
    __tablename__ = "business_units"

    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("business_units.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(191), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'office', 'agency'
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    # Branding
    branding_text_dark: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    branding_bg_light: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    branding_text_light: Mapped[Optional[str]] = mapped_column(
        String(12), nullable=True
    )
    branding_bg_dark: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    branding_logo_file_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )

    company: Mapped["Company"] = relationship(
        "Company", back_populates="business_units"
    )
    parent: Mapped[Optional["BusinessUnit"]] = relationship(
        "BusinessUnit", remote_side="BusinessUnit.id", back_populates="children"
    )
    children: Mapped[List["BusinessUnit"]] = relationship(
        "BusinessUnit", back_populates="parent"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="memberships_business_unit", back_populates="business_units"
    )


class CompanyUser(Base):
    __tablename__ = "company_user"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    basic_functions: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class BusinessUnitMembership(Base):
    __tablename__ = "memberships_business_unit"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    business_unit_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("business_units.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    role_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("roles.id"))
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
