import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.emission.schemas import ClientCreate, ClientResponse, EmissionRequest, EmissionResponse, PolicyResponse, StatusTransitionRequest
from app.modules.emission import service

router = APIRouter(prefix="/emission", tags=["Emission"])

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def register_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.register_client(db, data, current_user.id)

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.get_client(db, client_id)

@router.post("/issue", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def issue_policy(
    data: EmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.issue_policy(db, data, current_user.id)

@router.get("/policies", response_model=List[PolicyResponse])
async def list_policies(
    status: Optional[str] = None,
    client_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.list_policies(db, status=status, client_id=client_id)

@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    return await service.get_policy(db, policy_id)

@router.post("/policies/{policy_id}/transition", response_model=PolicyResponse)
async def change_policy_status(
    policy_id: uuid.UUID,
    data: StatusTransitionRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("ADMIN"))
):
    return await service.change_policy_status(db, policy_id, data, admin_user.id)

@router.get("/policies/{policy_id}/pdf")
async def download_policy_pdf(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR"))
):
    policy = await service.get_policy(db, policy_id)
    if not policy.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated for this policy")
    
    return FileResponse(
        path=policy.pdf_path,
        filename=f"{policy.policy_number}.pdf",
        media_type="application/pdf"
    )
