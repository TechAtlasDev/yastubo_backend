import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.plans.schemas import (
    ProductCreate,
    ProductResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
)
from app.modules.plans import service

# Product Router (Mainly for Admin/Configuration)
product_router = APIRouter(prefix="/products", tags=["Products"])


@product_router.get("/", response_model=List[ProductResponse])
async def list_products(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.list_products(db, active_only=active_only)


@product_router.post(
    "/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN")),
):
    return await service.create_product(db, data, admin_user.id)


@product_router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_product(db, product_id)


# Plans Router (Mainly for Pricing and compatibility)
plans_router = APIRouter(prefix="/plans", tags=["Plans"])


@plans_router.post("/calculate-price", response_model=PriceCalculationResponse)
async def calculate_price(
    data: PriceCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_price(db, data)


# Main router for app/main.py
router = APIRouter()
router.include_router(product_router)
router.include_router(plans_router)
