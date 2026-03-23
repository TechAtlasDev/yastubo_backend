import uuid
import os
import asyncio
from datetime import date, datetime, timedelta
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.emission.models import Client, Policy, PolicyStatusHistory
from app.modules.emission.schemas import ClientCreate, EmissionRequest, StatusTransitionRequest
from app.modules.emission import state_machine, pdf_generator
from app.modules.plans.models import Plan
from app.modules.plans import service as plans_service
from app.modules.plans import calculator
from app.modules.notifications.service import get_notifications_service
from app.modules.crm.service import sync_policy_to_crm, update_policy_stage_in_crm
from app.modules.crm.zoho_client import get_zoho_client
from app.modules.audit.decorator import audited

@audited(action="CLIENT_REGISTERED", entity="Client")
async def register_client(db: AsyncSession, data: ClientCreate, created_by: uuid.UUID) -> Client:
    # Check if email exists
    existing = await db.execute(select(Client).where(Client.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Client with this email already exists")
    
    client = Client(**data.model_dump(), created_by=created_by)
    db.add(client)
    
    await db.commit()
    await db.refresh(client)
    return client

async def get_client(db: AsyncSession, client_id: uuid.UUID) -> Client:
    res = await db.execute(select(Client).where(Client.id == client_id))
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@audited(action="POLICY_ISSUED", entity="Policy")
async def issue_policy(db: AsyncSession, data: EmissionRequest, issued_by: uuid.UUID) -> Policy:
    # 1. Get Client
    client = await get_client(db, data.client_id)
    
    # 2. Get Plan
    plan = await plans_service.get_plan(db, data.plan_id)
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Plan is inactive")
    
    # 3. Calculate Age at start_date
    age = data.start_date.year - client.birth_date.year - ((data.start_date.month, data.start_date.day) < (client.birth_date.month, client.birth_date.day))
    
    # 4. Validate eligibility
    if age > plan.max_entry_age:
        raise HTTPException(status_code=422, detail=f"Client age {age} exceeds max entry age {plan.max_entry_age}")
    
    config = next((cc for cc in plan.country_configs if cc.country_code == data.country_code and cc.is_available), None)
    if not config:
        raise HTTPException(status_code=422, detail=f"Plan not available in country {data.country_code}")
    
    # 5. Calculate price
    age_ranges = [{"min_age": ar.min_age, "max_age": ar.max_age, "surcharge_percentage": ar.surcharge_percentage} for ar in plan.age_ranges]
    country_override = Decimal(str(config.base_price_override)) if config.base_price_override is not None else None
    
    try:
        calc_result = calculator.calculate_price(
            base_price=Decimal(str(plan.base_price)),
            age=age,
            age_ranges=age_ranges,
            country_override=country_override
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # 6. Generate policy number
    year = datetime.now().year
    count_res = await db.execute(select(func.count(Policy.id)))
    counter = count_res.scalar() + 1
    policy_number = f"YAS-{year}-{counter:06d}"
    
    # 7. Snapshot
    plan_snapshot = {
        "name": plan.name,
        "base_price": float(plan.base_price),
        "age_ranges": [{"min": ar.min_age, "max": ar.max_age, "pct": float(ar.surcharge_percentage)} for ar in plan.age_ranges],
        "countries": [{"code": cc.country_code, "price": float(cc.base_price_override) if cc.base_price_override is not None else None} for cc in plan.country_configs],
        "coverages": [c.name for c in plan.coverages],
        "terms_es": plan.terms_es,
        "repatriation_countries": plan.repatriation_countries
    }
    
    # 8. Create Policy (DRAFT)
    end_date = data.start_date + timedelta(days=365) # 1 year by default
    policy = Policy(
        policy_number=policy_number,
        client_id=client.id,
        plan_id=plan.id,
        plan_version_snapshot=plan_snapshot,
        status=state_machine.PolicyStatus.DRAFT,
        base_price=float(calc_result["base_price"]),
        surcharge_amount=float(calc_result["age_surcharge_amount"]),
        final_price=float(calc_result["final_price"]),
        currency=plan.currency,
        country_code=data.country_code,
        insured_age=age,
        start_date=data.start_date,
        end_date=end_date,
        notes=data.notes,
        issued_by=issued_by,
        issued_at=datetime.now()
    )
    db.add(policy)
    await db.flush()
    
    # 9. History (INITIAL -> DRAFT)
    h1 = PolicyStatusHistory(policy_id=policy.id, from_status=None, to_status=state_machine.PolicyStatus.DRAFT, changed_by=issued_by, reason="Policy creation")
    db.add(h1)
    
    # 10. Transition to PENDING_PAYMENT
    old_status = policy.status
    new_status = state_machine.transition(old_status, state_machine.PolicyStatus.PENDING_PAYMENT)
    policy.status = new_status
    
    # 11. History (DRAFT -> PENDING_PAYMENT)
    h2 = PolicyStatusHistory(policy_id=policy.id, from_status=old_status, to_status=new_status, changed_by=issued_by, reason="Auto-transition to pending payment")
    db.add(h2)
    
    # 12. Generate PDF
    pdf_bytes = pdf_generator.generate_contract_pdf(policy, client, plan_snapshot)
    
    # 13. Save path
    policy.pdf_path = f"storage/policies/{policy_number}.pdf"
    
    # 14. Notifications
    notifications = get_notifications_service()
    await notifications.on_policy_issued(policy, client, pdf_bytes)
    
    await db.commit()

    # 15. CRM sync (best-effort, non-blocking)
    asyncio.create_task(
        sync_policy_to_crm(get_zoho_client(), policy, client, plan.name)
    )

    return await get_policy(db, policy.id)

async def get_policy(db: AsyncSession, policy_id: uuid.UUID) -> Policy:
    res = await db.execute(
        select(Policy)
        .where(Policy.id == policy_id)
        .options(
            selectinload(Policy.client),
            selectinload(Policy.status_history)
        )
    )
    policy = res.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

async def list_policies(db: AsyncSession, status: Optional[str] = None, client_id: Optional[uuid.UUID] = None) -> List[Policy]:
    query = select(Policy).options(selectinload(Policy.client), selectinload(Policy.status_history))
    if status:
        query = query.where(Policy.status == status)
    if client_id:
        query = query.where(Policy.client_id == client_id)
    
    res = await db.execute(query)
    return list(res.scalars().all())

@audited(action="POLICY_STATUS_CHANGED", entity="Policy")
async def change_policy_status(db: AsyncSession, policy_id: uuid.UUID, data: StatusTransitionRequest, changed_by: uuid.UUID) -> Policy:
    policy = await get_policy(db, policy_id)
    
    old_status = policy.status
    try:
        new_status = state_machine.transition(old_status, data.target_status)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    policy.status = new_status
    
    if new_status == state_machine.PolicyStatus.CANCELLED:
        policy.cancelled_at = datetime.now()
        policy.cancelled_by = changed_by
        
    history = PolicyStatusHistory(
        policy_id=policy.id,
        from_status=old_status,
        to_status=new_status,
        changed_by=changed_by,
        reason=data.reason
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(policy, ["status_history"])

    # Best-effort, non-blocking CRM stage update
    asyncio.create_task(update_policy_stage_in_crm(get_zoho_client(), policy))

    return policy
