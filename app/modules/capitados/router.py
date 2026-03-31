import uuid
from datetime import date
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.modules.capitados.service import CapitadosBatchService
from app.modules.capitados.schemas import BatchLogRead, BatchItemLogRead
from app.modules.capitados.models import CapitadosBatchLog, CapitadosBatchItemLog

router = APIRouter(prefix="/capitados", tags=["Capitados"])


@router.post("/batches/upload", response_model=BatchLogRead)
async def upload_batch(
    background_tasks: BackgroundTasks,
    company_id: uuid.UUID = Form(...),
    coverage_month: date = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an Excel file to process a batch of capitados for a company and month.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload an Excel file."
        )

    content = await file.read()

    # Create log entry
    batch = await CapitadosBatchService.create_batch_log(
        db=db,
        company_id=company_id,
        coverage_month=coverage_month,
        original_filename=file.filename,
    )

    # Process in background
    background_tasks.add_task(
        CapitadosBatchService.process_batch, db, batch.id, content
    )

    return batch


@router.get("/batches/{batch_id}", response_model=BatchLogRead)
async def get_batch_status(batch_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Get the status and summary of a processing batch.
    """
    batch = await db.get(CapitadosBatchLog, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/batches/{batch_id}/items", response_model=List[BatchItemLogRead])
async def get_batch_items(
    batch_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed row-by-row logs for a batch.
    """
    stmt = (
        select(CapitadosBatchItemLog)
        .where(CapitadosBatchItemLog.batch_id == batch_id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()
