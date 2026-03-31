from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.finance.service import CommissionService
from app.modules.finance.schemas import (
    CommissionDispersionRequest,
    CommissionSplit,
    CurrencyResponse,
    UnitOfMeasureResponse,
)
from app.modules.finance.models import Currency, UnitOfMeasure
from sqlalchemy import select

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.post("/commissions/calculate", response_model=List[CommissionSplit])
async def calculate_commissions(
    data: CommissionDispersionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate commission dispersion for a given amount and company/BU.
    """
    try:
        return await CommissionService.calculate_dispersion(
            db, data.amount, data.company_id, data.business_unit_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/currencies", response_model=List[CurrencyResponse])
async def list_currencies(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Currency).where(Currency.is_active.is_(True)))
    return res.scalars().all()


@router.get("/units-of-measure", response_model=List[UnitOfMeasureResponse])
async def list_units_of_measure(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(UnitOfMeasure).where(UnitOfMeasure.status == "active")
    )
    return res.scalars().all()
