from typing import List, Optional
from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    Text,
    JSON,
    DateTime,
    func,
    CHAR,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CountryZone(Base):
    """Association table between countries and zones."""

    __tablename__ = "country_zone"

    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), primary_key=True
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class GeographyBase(Base):
    """Base class for geography models with integer IDs."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Country(GeographyBase):
    """Model representing a country as defined in the legacy schema."""

    __tablename__ = "countries"

    name: Mapped[dict] = mapped_column(JSON, nullable=False)
    iso2: Mapped[Optional[str]] = mapped_column(CHAR(2), unique=True, nullable=True)
    iso3: Mapped[Optional[str]] = mapped_column(CHAR(3), unique=True, nullable=True)
    continent_code: Mapped[str] = mapped_column(String(2), index=True, nullable=False)
    phone_code: Mapped[Optional[str]] = mapped_column(
        String(10), index=True, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    zones: Mapped[List["Zone"]] = relationship(
        secondary="country_zone", back_populates="countries"
    )

    def __repr__(self) -> str:
        return f"<Country(id={self.id}, iso2={self.iso2})>"


class Zone(GeographyBase):
    """Model representing a geographic zone (regions, continents, etc.)."""

    __tablename__ = "zones"

    name: Mapped[str] = mapped_column(String(191), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    countries: Mapped[List["Country"]] = relationship(
        secondary="country_zone", back_populates="zones"
    )

    def __repr__(self) -> str:
        return f"<Zone(id={self.id}, name={self.name})>"
