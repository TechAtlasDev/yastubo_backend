from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.geography import service, schemas

router = APIRouter(prefix="/geography", tags=["Geography"])


# --- Countries ---


@router.post(
    "/countries", response_model=schemas.Country, status_code=status.HTTP_201_CREATED
)
async def create_country(
    data: schemas.CountryCreate,
    db: AsyncSession = Depends(get_db),
    # current_user=Depends(get_current_active_user), # Uncomment for auth
):
    """Create a new country."""
    return await service.create_country(db, data)


@router.get("/countries", response_model=List[schemas.Country])
async def list_countries(
    active_only: bool = True,
    continent: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all countries."""
    return await service.list_countries(db, active_only, continent)


@router.get("/countries/{country_id}", response_model=schemas.CountryWithZones)
async def get_country(
    country_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get country by ID with its zones."""
    return await service.get_country(db, country_id)


@router.patch("/countries/{country_id}", response_model=schemas.Country)
async def update_country(
    country_id: int,
    data: schemas.CountryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update country details."""
    return await service.update_country(db, country_id, data)


# --- Zones ---


@router.post("/zones", response_model=schemas.Zone, status_code=status.HTTP_201_CREATED)
async def create_zone(
    data: schemas.ZoneCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new geographic zone."""
    return await service.create_zone(db, data)


@router.get("/zones", response_model=List[schemas.Zone])
async def list_zones(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all zones."""
    return await service.list_zones(db, active_only)


@router.get("/zones/{zone_id}", response_model=schemas.ZoneWithCountries)
async def get_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get zone by ID with its countries."""
    return await service.get_zone(db, zone_id)


@router.patch("/zones/{zone_id}", response_model=schemas.Zone)
async def update_zone(
    zone_id: int,
    data: schemas.ZoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update zone details."""
    return await service.update_zone(db, zone_id, data)


# --- Relationships ---


@router.post(
    "/zones/{zone_id}/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def add_country_to_zone(
    zone_id: int,
    country_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Associate a country with a zone."""
    await service.add_country_to_zone(db, country_id, zone_id)


@router.delete(
    "/zones/{zone_id}/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_country_from_zone(
    zone_id: int,
    country_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Remove a country from a zone."""
    await service.remove_country_from_zone(db, country_id, zone_id)
