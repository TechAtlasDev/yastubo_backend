import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from app.modules.emission.passbook_service import get_passbook_service, PassbookService
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import User
from app.modules.emission import schemas, service
from app.modules.emission.pdf_service import PDFService

router = APIRouter(prefix="/emission", tags=["Emission"])


@router.post(
    "/clients",
    response_model=schemas.ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_client(
    data: schemas.ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    company_id = current_user.companies[0].id
    return await service.register_client(db, data, current_user.id, company_id)


@router.get("/clients/{client_id}", response_model=schemas.ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    return await service.get_client(db, client_id)


@router.post(
    "/issue", response_model=schemas.PolicyResponse, status_code=status.HTTP_201_CREATED
)
async def issue_policy(
    data: schemas.EmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    return await service.issue_policy(db, data, current_user.id)


@router.get("/policies", response_model=List[schemas.PolicyResponse])
async def list_policies(
    status: Optional[str] = None,
    search: Optional[str] = None,
    client_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    """
    Lista las pólizas de la compañía del usuario. Soporta filtrado por estado, búsqueda o ID de cliente.
    """
    company_id = current_user.companies[0].id
    return await service.list_policies(
        db, company_id, status=status, search=search, client_id=client_id
    )


@router.get("/stats", response_model=schemas.EmissionStats)
async def get_emission_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    company_id = current_user.companies[0].id
    return await service.get_stats(db, company_id)


@router.get("/policies/{policy_id}", response_model=schemas.PolicyResponse)
async def get_policy(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    return await service.get_policy(db, policy_id)


@router.post("/policies/{policy_id}/transition", response_model=schemas.PolicyResponse)
async def change_policy_status(
    policy_id: uuid.UUID,
    data: schemas.StatusTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    return await service.change_policy_status(db, policy_id, data, current_user.id)


@router.post(
    "/beneficiaries/{beneficiary_id}/mark-deceased",
    response_model=schemas.BeneficiaryResponse,
)
async def mark_beneficiary_deceased(
    beneficiary_id: uuid.UUID,
    data: schemas.DeceasedReport,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN")
    ),  # Only admin/system can mark deceased
):
    """
    Mark a beneficiary as deceased.
    Triggered by CRM write-back or internal management.
    """
    return await service.mark_beneficiary_deceased(db, beneficiary_id, data.reported_by)


@router.get("/policies/{policy_id}/pdf")
async def download_policy_pdf(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    pdf_bytes = await PDFService.generate_policy_certificate(db, policy_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=policy_{policy_id}.pdf"},
    )


@router.get("/policies/{policy_id}/passbook")
async def get_policy_passbook(
    policy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    pass_service: PassbookService = Depends(get_passbook_service),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    policy = await service.get_policy(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Multi-tenancy check
    if not any(ws.id == policy.company_id for ws in current_user.companies):
        raise HTTPException(
            status_code=403, detail="You do not have access to this policy"
        )

    pass_bytes = await pass_service.generate_policy_pass(policy, policy.client)

    return Response(
        content=pass_bytes,
        media_type="application/vnd.apple.pkpass",
        headers={
            "Content-Disposition": f"attachment; filename=policy_{policy.policy_number}.pkpass"
        },
    )


@router.post("/bulk-upload", response_model=schemas.BulkEmissionResponse)
async def bulk_upload_beneficiaries(
    client_id: uuid.UUID = Form(...),
    plan_id: uuid.UUID = Form(...),
    plan_version_id: uuid.UUID = Form(...),
    country_code: str = Form(...),
    start_date: str = Form(...),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "VENDEDOR")),
):
    """
    Bulk upload beneficiaries from an Excel file.
    Expects columns: first_name, last_name, date_of_birth (YYYY-MM-DD), kinship_type, country_of_residence.
    """
    from datetime import datetime

    data = schemas.BulkEmissionRequest(
        client_id=client_id,
        plan_id=plan_id,
        plan_version_id=plan_version_id,
        country_code=country_code,
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        notes=notes,
    )

    file_content = await file.read()
    return await service.bulk_issue_policy(db, data, file_content, current_user.id)
