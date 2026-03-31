import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    Text,
    JSON,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.organizations.models import Company, BusinessUnit
    from app.modules.auth.models import User


class FinanceBase(Base):
    """Base class for finance models with integer IDs (matching legacy)."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class Currency(FinanceBase):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(
        String(3), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Currency(code={self.code})>"


class UnitOfMeasure(FinanceBase):
    __tablename__ = "units_of_measure"

    name: Mapped[dict] = mapped_column(JSON, nullable=False)  # i18n name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measure_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, default="active")

    def __repr__(self) -> str:
        return f"<UnitOfMeasure(id={self.id}, measure_type={self.measure_type})>"


class CompanyCommissionUser(BaseModel):
    """Commission percentages for actors at the Company level."""

    __tablename__ = "company_commission_users"

    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    commission_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=0.0
    )

    company: Mapped["Company"] = relationship("Company")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_commission_user"),
    )


class BusinessUnitCommissionUser(BaseModel):
    """Commission percentages for actors at the Business Unit level."""

    __tablename__ = "business_unit_commission_users"

    business_unit_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("business_units.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    commission_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=0.0
    )

    business_unit: Mapped["BusinessUnit"] = relationship("BusinessUnit")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("business_unit_id", "user_id", name="uq_bu_commission_user"),
    )
