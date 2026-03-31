import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.organizations.models import Company, BusinessUnit
from app.modules.organizations.schemas import CompanyCreate, BusinessUnitCreate
from app.modules.audit.decorator import audited


@audited(action="COMPANY_CREATED", entity="Company")
async def create_company(db: AsyncSession, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    db.add(company)
    await db.commit()
    # Reload with business_units to avoid lazy load issues in response serialization
    result = await db.execute(
        select(Company)
        .where(Company.id == company.id)
        .options(selectinload(Company.business_units))
    )
    return result.scalar_one()


async def list_companies(db: AsyncSession) -> List[Company]:
    result = await db.execute(
        select(Company).options(selectinload(Company.business_units))
    )
    return list(result.scalars().all())


async def get_company(db: AsyncSession, company_id: uuid.UUID) -> Company:
    result = await db.execute(
        select(Company)
        .where(Company.id == company_id)
        .options(selectinload(Company.business_units))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return company


@audited(action="BUSINESS_UNIT_CREATED", entity="BusinessUnit")
async def create_business_unit(
    db: AsyncSession, company_id: uuid.UUID, data: BusinessUnitCreate
) -> BusinessUnit:
    # Verify company exists
    await get_company(db, company_id)

    bu = BusinessUnit(company_id=company_id, **data.model_dump())
    db.add(bu)
    await db.commit()
    await db.refresh(bu)
    return bu


async def list_business_units(
    db: AsyncSession, company_id: uuid.UUID
) -> List[BusinessUnit]:
    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.company_id == company_id)
    )
    return list(result.scalars().all())
