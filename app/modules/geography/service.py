from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.modules.geography.models import Country, Zone, CountryZone
from app.modules.geography.schemas import (
    CountryCreate,
    CountryUpdate,
    ZoneCreate,
    ZoneUpdate,
)


# --- Country Services ---


async def create_country(db: AsyncSession, data: CountryCreate) -> Country:
    country = Country(
        name=data.name,
        iso2=data.iso2,
        iso3=data.iso3,
        continent_code=data.continent_code,
        phone_code=data.phone_code,
        is_active=data.is_active,
    )
    db.add(country)
    await db.commit()
    await db.refresh(country)
    return country


async def get_country(db: AsyncSession, country_id: int) -> Country:
    result = await db.execute(
        select(Country)
        .where(Country.id == country_id)
        .options(selectinload(Country.zones))
    )
    country = result.scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


async def list_countries(
    db: AsyncSession, active_only: bool = True, continent_code: Optional[str] = None
) -> List[Country]:
    query = select(Country).options(selectinload(Country.zones))
    if active_only:
        query = query.where(Country.is_active)
    if continent_code:
        query = query.where(Country.continent_code == continent_code)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_country(
    db: AsyncSession, country_id: int, data: CountryUpdate
) -> Country:
    country = await get_country(db, country_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(country, field, value)

    await db.commit()
    await db.refresh(country)
    return country


# --- Zone Services ---


async def create_zone(db: AsyncSession, data: ZoneCreate) -> Zone:
    zone = Zone(
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


async def get_zone(db: AsyncSession, zone_id: int) -> Zone:
    result = await db.execute(
        select(Zone).where(Zone.id == zone_id).options(selectinload(Zone.countries))
    )
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


async def list_zones(db: AsyncSession, active_only: bool = True) -> List[Zone]:
    query = select(Zone).options(selectinload(Zone.countries))
    if active_only:
        query = query.where(Zone.is_active)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_zone(db: AsyncSession, zone_id: int, data: ZoneUpdate) -> Zone:
    zone = await get_zone(db, zone_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.commit()
    await db.refresh(zone)
    return zone


# --- Relationship Services ---


async def add_country_to_zone(db: AsyncSession, country_id: int, zone_id: int) -> None:
    # Verify both exist
    await get_country(db, country_id)
    await get_zone(db, zone_id)

    # Check if already exists
    result = await db.execute(
        select(CountryZone).where(
            CountryZone.country_id == country_id, CountryZone.zone_id == zone_id
        )
    )
    if result.scalar_one_or_none():
        return

    assoc = CountryZone(country_id=country_id, zone_id=zone_id)
    db.add(assoc)
    await db.commit()


async def remove_country_from_zone(
    db: AsyncSession, country_id: int, zone_id: int
) -> None:
    await db.execute(
        delete(CountryZone).where(
            CountryZone.country_id == country_id, CountryZone.zone_id == zone_id
        )
    )
    await db.commit()
