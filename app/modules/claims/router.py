import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.claims import schemas, service

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post(
    "/", response_model=schemas.ClaimResponse, status_code=status.HTTP_201_CREATED
)
async def create_claim(
    claim_in: schemas.ClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create_claim(db=db, claim_in=claim_in, user_id=current_user.id)


@router.get("/{claim_id}", response_model=schemas.ClaimResponse)
async def get_claim(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_claim(db=db, claim_id=claim_id)


@router.patch("/{claim_id}/status", response_model=schemas.ClaimResponse)
async def update_claim_status(
    claim_id: uuid.UUID,
    status_update: schemas.ClaimUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.update_claim_status(
        db=db, claim_id=claim_id, status_update=status_update, user_id=current_user.id
    )


@router.post(
    "/{claim_id}/expenses",
    response_model=schemas.ClaimExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_expense(
    claim_id: uuid.UUID,
    expense_in: schemas.ClaimExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.add_claim_expense(
        db=db, claim_id=claim_id, expense_in=expense_in, user_id=current_user.id
    )
