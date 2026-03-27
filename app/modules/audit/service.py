import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.modules.audit.models import AuditLog


async def log(
    db: AsyncSession,
    action: str,
    entity: str,
    user_id: Optional[uuid.UUID] = None,
    entity_id: Optional[uuid.UUID] = None,
    old_values: Optional[dict[str, Any]] = None,
    new_values: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None,
    extra: Optional[dict[str, Any]] = None,
    details: Optional[str] = None,
) -> AuditLog:
    ip_address = None
    user_agent = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    audit_log = AuditLog(
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id else None,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        old_values=old_values,
        new_values=new_values,
        extra=extra,
        details=details,
    )

    db.add(audit_log)
    # We do NOT commit here to avoid breaking the caller's transaction
    await db.flush()
    await db.refresh(audit_log)
    return audit_log


async def list_audit_logs(
    db: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    filters = []

    if user_id:
        filters.append(AuditLog.user_id == user_id)
    if action:
        filters.append(AuditLog.action == action)
    if entity:
        filters.append(AuditLog.entity == entity)
    if entity_id:
        filters.append(AuditLog.entity_id == str(entity_id))
    if date_from:
        filters.append(AuditLog.created_at >= date_from)
    if date_to:
        filters.append(AuditLog.created_at <= date_to)

    if filters:
        query = query.where(and_(*filters))

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return items, total
