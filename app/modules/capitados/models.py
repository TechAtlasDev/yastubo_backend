from uuid import UUID
from datetime import date, datetime
from typing import Optional
from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    Text,
    JSON,
    Date,
    DateTime,
    Boolean,
    Integer,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import BaseModel, GUID


class CapitadosVoidReason(BaseModel):
    __tablename__ = "capitados_void_reasons"

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class CapitadosBatchLog(BaseModel):
    __tablename__ = "capitados_batch_logs"

    company_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("companies.id"), nullable=False
    )
    coverage_month: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="excel", nullable=False)
    source_file_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    reconciliation_status: Mapped[str] = mapped_column(
        String(32), default="pendiente", nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rolled_back_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )

    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_duplicated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_incongruences: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_plan_errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_rolled_back: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_any_month_allowed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    cutoff_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class CapitadosProductInsured(BaseModel):
    __tablename__ = "capitados_product_insureds"

    company_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("companies.id"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("products.id"), nullable=False
    )
    document_number: Mapped[str] = mapped_column(String(64), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    residence_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )
    repatriation_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )
    age_reported: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rolled_back_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )


class CapitadosContract(BaseModel):
    __tablename__ = "capitados_contracts"

    # 'uuid' is for legacy compatibility, but BaseModel provides 'id' (GUID)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("companies.id"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("products.id"), nullable=False
    )
    person_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("capitados_product_insureds.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    entry_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    wtime_suicide_ends_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    wtime_preexisting_conditions_ends_at: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )
    wtime_accident_ends_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    terminated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    termination_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rolled_back_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )


class CapitadosMonthlyRecord(BaseModel):
    __tablename__ = "capitados_monthly_records"

    company_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("companies.id"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("products.id"), nullable=False
    )
    person_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("capitados_product_insureds.id"), nullable=False
    )
    contract_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("capitados_contracts.id"), nullable=False
    )
    coverage_month: Mapped[date] = mapped_column(Date, nullable=False)
    plan_version_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("plan_versions.id"), nullable=False
    )
    load_batch_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("capitados_batch_logs.id"), nullable=False
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    age_reported: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    residence_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )
    repatriation_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )

    price_base: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    price_source: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    age_surcharge_rule_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("plan_version_age_surcharges.id"), nullable=True
    )
    age_surcharge_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    age_surcharge_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    price_final: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rolled_back_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )


class CapitadosBatchItemLog(BaseModel):
    __tablename__ = "capitados_batch_item_logs"

    batch_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("capitados_batch_logs.id"), nullable=False
    )
    sheet_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    row_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    product_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("products.id"), nullable=True
    )
    plan_version_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("plan_versions.id"), nullable=True
    )

    residence_raw: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    residence_code_extracted: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True
    )
    repatriation_raw: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    repatriation_code_extracted: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True
    )

    residence_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )
    repatriation_country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id"), nullable=True
    )

    document_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    age_reported: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    result: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rejection_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    rejection_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    person_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("capitados_product_insureds.id"), nullable=True
    )
    contract_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("capitados_contracts.id"), nullable=True
    )
    monthly_record_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("capitados_monthly_records.id"), nullable=True
    )
    duplicated_record_id: Mapped[Optional[UUID]] = mapped_column(
        GUID(), ForeignKey("capitados_monthly_records.id"), nullable=True
    )
