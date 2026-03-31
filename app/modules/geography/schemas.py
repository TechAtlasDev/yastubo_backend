from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GeographyBase(BaseModel):
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class ZoneBase(GeographyBase):
    name: str
    description: Optional[str] = None


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class Zone(ZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CountryBase(GeographyBase):
    name: Dict[str, str]  # JSON: {"es": "...", "en": "..."}
    iso2: Optional[str] = None
    iso3: Optional[str] = None
    continent_code: str
    phone_code: Optional[str] = None


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    iso2: Optional[str] = None
    iso3: Optional[str] = None
    continent_code: Optional[str] = None
    phone_code: Optional[str] = None
    is_active: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class Country(CountryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CountryWithZones(Country):
    zones: List[Zone] = []


class ZoneWithCountries(Zone):
    countries: List[Country] = []
