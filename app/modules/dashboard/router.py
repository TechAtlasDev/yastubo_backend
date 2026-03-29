from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import User
from app.modules.dashboard import schemas, service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=schemas.DashboardKPIMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """
    Get KPI metrics for the current workspace dashboard.
    Only accessible by ADMIN.
    """
    if not current_user.workspaces:
        raise HTTPException(status_code=404, detail="No workspace found for this user")
    workspace_id = current_user.workspaces[0].id
    return await service.get_dashboard_metrics(db, workspace_id)
