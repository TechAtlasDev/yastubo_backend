import uuid
from typing import List, Optional
from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    Integer,
    Numeric,
    Text,
    JSON,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID


class Product(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product_type: Mapped[str] = mapped_column(String(50), default="repatriation")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    plans: Mapped[List["Plan"]] = relationship(
        "Plan", back_populates="product", cascade="all, delete-orphan"
    )


class Plan(BaseModel):
    __tablename__ = "plans"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped["Product"] = relationship("Product", back_populates="plans")
    versions: Mapped[List["PlanVersion"]] = relationship(
        "PlanVersion", back_populates="plan", cascade="all, delete-orphan"
    )


class PlanVersion(BaseModel):
    __tablename__ = "plan_versions"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Financials
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    public_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Rules
    max_entry_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_renewal_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Vesting Periods (Wait times)
    wtime_suicide: Mapped[int] = mapped_column(Integer, default=365)
    wtime_preexisting: Mapped[int] = mapped_column(Integer, default=180)
    wtime_accident: Mapped[int] = mapped_column(Integer, default=0)

    # Content
    terms_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"))

    plan: Mapped["Plan"] = relationship("Plan", back_populates="versions")
    age_surcharges: Mapped[List["PlanVersionAgeSurcharge"]] = relationship(
        "PlanVersionAgeSurcharge",
        back_populates="plan_version",
        cascade="all, delete-orphan",
    )
    countries: Mapped[List["PlanVersionCountry"]] = relationship(
        "PlanVersionCountry",
        back_populates="plan_version",
        cascade="all, delete-orphan",
    )
    coverages: Mapped[List["PlanVersionCoverage"]] = relationship(
        "PlanVersionCoverage",
        back_populates="plan_version",
        cascade="all, delete-orphan",
    )
    repatriation_countries: Mapped[List["PlanVersionRepatriationCountry"]] = (
        relationship(
            "PlanVersionRepatriationCountry",
            back_populates="plan_version",
            cascade="all, delete-orphan",
        )
    )

    __table_args__ = (
        UniqueConstraint("plan_id", "version_number", name="uq_plan_version"),
    )


class PlanVersionAgeSurcharge(BaseModel):
    __tablename__ = "plan_version_age_surcharges"

    plan_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plan_versions.id", ondelete="CASCADE"), nullable=False
    )
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)
    surcharge_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    plan_version: Mapped["PlanVersion"] = relationship(
        "PlanVersion", back_populates="age_surcharges"
    )

    __table_args__ = (CheckConstraint("min_age <= max_age", name="check_age_order"),)


class PlanVersionCountry(BaseModel):
    __tablename__ = "plan_version_countries"

    plan_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plan_versions.id", ondelete="CASCADE"), nullable=False
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_override: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    plan_version: Mapped["PlanVersion"] = relationship(
        "PlanVersion", back_populates="countries"
    )

    __table_args__ = (
        UniqueConstraint(
            "plan_version_id", "country_code", name="uq_plan_version_country"
        ),
    )


class PlanVersionCoverage(BaseModel):
    __tablename__ = "plan_version_coverages"

    plan_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plan_versions.id", ondelete="CASCADE"), primary_key=True
    )
    coverage_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("coverages.id", ondelete="CASCADE"), primary_key=True
    )
    value_int: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    value_decimal: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    value_text: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_included: Mapped[bool] = mapped_column(Boolean, default=True)

    plan_version: Mapped["PlanVersion"] = relationship(
        "PlanVersion", back_populates="coverages"
    )
    coverage: Mapped["Coverage"] = relationship("Coverage")


class PlanVersionRepatriationCountry(BaseModel):
    __tablename__ = "plan_version_repatriation_countries"

    plan_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plan_versions.id", ondelete="CASCADE"), nullable=False
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)

    plan_version: Mapped["PlanVersion"] = relationship(
        "PlanVersion", back_populates="repatriation_countries"
    )


class Coverage(BaseModel):
    __tablename__ = "coverages"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
