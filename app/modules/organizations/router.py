import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.organizations.schemas import (
    CompanyCreate,
    CompanyResponse,
    BusinessUnitCreate,
    BusinessUnitResponse,
)
from app.modules.organizations import service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN")),
):
    """
    Create a new company. Requires ADMIN role.
    """
    return await service.create_company(db, data)


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all companies. Requires authentication.
    """
    return await service.list_companies(db)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a company, including its business units.
    """
    return await service.get_company(db, company_id)


@router.post(
    "/companies/{company_id}/business-units",
    response_model=BusinessUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_business_unit(
    company_id: uuid.UUID,
    data: BusinessUnitCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN")),
):
    """
    Create a new business unit under a company. Requires ADMIN role.
    """
    return await service.create_business_unit(db, company_id, data)


@router.get(
    "/companies/{company_id}/business-units",
    response_model=List[BusinessUnitResponse],
)
async def list_business_units(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all business units for a given company.
    """
    return await service.list_business_units(db, company_id)
