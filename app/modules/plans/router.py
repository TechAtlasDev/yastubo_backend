import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.plans.schemas import PlanCreate, PlanUpdate, PlanResponse, PriceCalculationRequest, PriceCalculationResponse
from app.modules.plans import service
from app.modules.plans.models import PlanVersion

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.get("/", response_model=List[PlanResponse])
async def list_plans(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.list_plans(db, active_only=active_only)

@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.create_plan(db, data, admin_user.id)

@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_plan(db, plan_id)

@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.update_plan(db, plan_id, data, admin_user.id)

@router.patch("/{plan_id}/toggle", response_model=PlanResponse)
async def toggle_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.toggle_plan(db, plan_id, admin_user.id)

@router.post("/calculate-price", response_model=PriceCalculationResponse)
async def calculate_price(
    data: PriceCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_price(db, data)

@router.get("/{plan_id}/versions")
async def list_plan_versions(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    result = await db.execute(
        select(PlanVersion).where(PlanVersion.plan_id == plan_id).order_by(PlanVersion.version_number.desc())
    )
    return result.scalars().all()
