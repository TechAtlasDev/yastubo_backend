import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Boolean, Integer, Numeric, Text, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID
from app.core.database import Base

class PlanCoverage(Base):
    __tablename__ = "plan_coverages"

    plan_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("plans.id", ondelete="CASCADE"), primary_key=True)
    coverage_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("coverages.id", ondelete="CASCADE"), primary_key=True)
    override_limit: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    is_included: Mapped[bool] = mapped_column(Boolean, default=True)

class Coverage(BaseModel):
    __tablename__ = "coverages"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    limit_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    limit_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # USD, días, eventos
    notes_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    plans: Mapped[List["Plan"]] = relationship(
        secondary="plan_coverages", back_populates="coverages"
    )

class AgeRange(BaseModel):
    __tablename__ = "age_ranges"

    plan_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)
    surcharge_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="age_ranges")

    __table_args__ = (
        CheckConstraint("min_age < max_age", name="check_age_order"),
        CheckConstraint("surcharge_percentage >= 0", name="check_positive_surcharge"),
    )

class CountryConfig(BaseModel):
    __tablename__ = "country_configs"

    plan_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_price_override: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="country_configs")

    __table_args__ = (
        UniqueConstraint("plan_id", "country_code", name="uq_plan_country"),
    )

class Plan(BaseModel):
    __tablename__ = "plans"

    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_entry_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_renewal_age: Mapped[int] = mapped_column(Integer, nullable=False)
    repatriation_countries: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    terms_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    versions: Mapped[List["PlanVersion"]] = relationship("PlanVersion", back_populates="plan", cascade="all, delete-orphan")
    coverages: Mapped[List["Coverage"]] = relationship(
        secondary="plan_coverages", back_populates="plans"
    )
    age_ranges: Mapped[List["AgeRange"]] = relationship("AgeRange", back_populates="plan", cascade="all, delete-orphan")
    country_configs: Mapped[List["CountryConfig"]] = relationship("CountryConfig", back_populates="plan", cascade="all, delete-orphan")

class PlanVersion(BaseModel):
    __tablename__ = "plan_versions"

    plan_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("plan_id", "version_number", name="uq_plan_version"),
    )
