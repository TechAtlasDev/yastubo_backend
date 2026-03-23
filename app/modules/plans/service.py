import uuid
import json
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.plans.models import Plan, PlanVersion, Coverage, AgeRange, CountryConfig, PlanCoverage
from app.modules.plans.schemas import PlanCreate, PlanUpdate, PriceCalculationRequest, PriceCalculationResponse
from app.modules.plans import calculator
from app.modules.audit.decorator import audited

@audited(action="PLAN_CREATED", entity="Plan")
async def create_plan(db: AsyncSession, data: PlanCreate, created_by: uuid.UUID) -> Plan:
    plan = Plan(
        name=data.name,
        description=data.description,
        base_price=float(data.base_price),
        currency=data.currency,
        max_entry_age=data.max_entry_age,
        max_renewal_age=data.max_renewal_age,
        repatriation_countries=data.repatriation_countries,
        terms_es=data.terms_es,
        terms_en=data.terms_en,
    )
    db.add(plan)
    await db.flush()

    # Add AgeRanges
    for ar in data.age_ranges:
        age_range = AgeRange(
            plan_id=plan.id,
            min_age=ar.min_age,
            max_age=ar.max_age,
            surcharge_percentage=float(ar.surcharge_percentage)
        )
        db.add(age_range)

    # Add CountryConfigs
    for cc in data.country_configs:
        country_config = CountryConfig(
            plan_id=plan.id,
            country_code=cc.country_code,
            country_name=cc.country_name,
            base_price_override=float(cc.base_price_override) if cc.base_price_override is not None else None,
            is_available=cc.is_available
        )
        db.add(country_config)

    # Associate Coverages
    for cov_id in data.coverage_ids:
        # Verify coverage exists
        cov_res = await db.execute(select(Coverage).where(Coverage.id == cov_id))
        if not cov_res.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Coverage {cov_id} not found")
        
        plan_cov = PlanCoverage(plan_id=plan.id, coverage_id=cov_id)
        db.add(plan_cov)

    await db.flush()
    await db.refresh(plan, ["age_ranges", "country_configs", "coverages"])

    # Create Initial Version
    snapshot = {
        "name": plan.name,
        "base_price": float(plan.base_price),
        "age_ranges": [{"min": ar.min_age, "max": ar.max_age, "pct": float(ar.surcharge_percentage)} for ar in plan.age_ranges],
        "countries": [{"code": cc.country_code, "price": float(cc.base_price_override) if cc.base_price_override is not None else None} for cc in plan.country_configs],
        "coverages": [c.name for c in plan.coverages]
    }
    
    version = PlanVersion(
        plan_id=plan.id,
        version_number=1,
        snapshot=snapshot,
        created_by=created_by
    )
    db.add(version)

    await db.commit()
    return plan

async def get_plan(db: AsyncSession, plan_id: uuid.UUID) -> Plan:
    result = await db.execute(
        select(Plan)
        .where(Plan.id == plan_id)
        .options(
            selectinload(Plan.age_ranges),
            selectinload(Plan.country_configs),
            selectinload(Plan.coverages),
            selectinload(Plan.versions)
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Calculate current version
    plan.current_version = max([v.version_number for v in plan.versions]) if plan.versions else 1
    return plan

async def list_plans(db: AsyncSession, active_only: bool = True) -> List[Plan]:
    query = select(Plan).options(
        selectinload(Plan.age_ranges),
        selectinload(Plan.country_configs),
        selectinload(Plan.coverages),
        selectinload(Plan.versions)
    )
    if active_only:
        query = query.where(Plan.is_active == True)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    for p in plans:
        p.current_version = max([v.version_number for v in p.versions]) if p.versions else 1
    return list(plans)

@audited(action="PLAN_UPDATED", entity="Plan")
async def update_plan(db: AsyncSession, plan_id: uuid.UUID, data: PlanUpdate, updated_by: uuid.UUID) -> Plan:
    plan = await get_plan(db, plan_id)
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Simple fields
    for field in ["name", "description", "base_price", "currency", "max_entry_age", "max_renewal_age", "repatriation_countries", "terms_es", "terms_en"]:
        if field in update_data:
            val = update_data[field]
            if field == "base_price":
                val = float(val)
            setattr(plan, field, val)

    # Complex fields (replace strategy for simplicity in this MVP)
    if "age_ranges" in update_data:
        # Delete old
        for ar in plan.age_ranges:
            await db.delete(ar)
        # Add new
        for ar in data.age_ranges:
            db.add(AgeRange(plan_id=plan.id, min_age=ar.min_age, max_age=ar.max_age, surcharge_percentage=float(ar.surcharge_percentage)))

    if "country_configs" in update_data:
        for cc in plan.country_configs:
            await db.delete(cc)
        for cc in data.country_configs:
            db.add(CountryConfig(plan_id=plan.id, country_code=cc.country_code, country_name=cc.country_name, base_price_override=float(cc.base_price_override) if cc.base_price_override is not None else None, is_available=cc.is_available))

    if "coverage_ids" in update_data:
        # Clear association
        await db.execute(PlanCoverage.__table__.delete().where(PlanCoverage.plan_id == plan.id))
        for cov_id in data.coverage_ids:
            db.add(PlanCoverage(plan_id=plan.id, coverage_id=cov_id))

    await db.flush()
    await db.refresh(plan, ["age_ranges", "country_configs", "coverages", "versions"])

    # New Version
    next_version = (max([v.version_number for v in plan.versions]) if plan.versions else 0) + 1
    snapshot = {
        "name": plan.name,
        "base_price": float(plan.base_price),
        "age_ranges": [{"min": ar.min_age, "max": ar.max_age, "pct": float(ar.surcharge_percentage)} for ar in plan.age_ranges],
        "countries": [{"code": cc.country_code, "price": float(cc.base_price_override) if cc.base_price_override is not None else None} for cc in plan.country_configs],
        "coverages": [c.name for c in plan.coverages]
    }
    
    version = PlanVersion(
        plan_id=plan.id,
        version_number=next_version,
        snapshot=snapshot,
        created_by=updated_by
    )
    db.add(version)

    await db.commit()
    plan.current_version = next_version
    return plan

@audited(action="PLAN_TOGGLED", entity="Plan")
async def toggle_plan(db: AsyncSession, plan_id: uuid.UUID, updated_by: uuid.UUID) -> Plan:
    plan = await get_plan(db, plan_id)
    plan.is_active = not plan.is_active
    
    await db.commit()
    return plan

async def get_price(db: AsyncSession, data: PriceCalculationRequest) -> PriceCalculationResponse:
    plan = await get_plan(db, data.plan_id)
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Plan is not active")
    
    # Validate country
    config = next((cc for cc in plan.country_configs if cc.country_code == data.country_code), None)
    if not config or not config.is_available:
        raise HTTPException(status_code=422, detail=f"Plan not available in country {data.country_code}")
    
    # Validate age
    if data.age > plan.max_entry_age:
        raise HTTPException(status_code=422, detail=f"Age {data.age} exceeds max entry age {plan.max_entry_age}")

    # Prepare for calculator
    age_ranges = [{"min_age": ar.min_age, "max_age": ar.max_age, "surcharge_percentage": ar.surcharge_percentage} for ar in plan.age_ranges]
    country_override = Decimal(str(config.base_price_override)) if config.base_price_override is not None else None
    
    try:
        calc_result = calculator.calculate_price(
            base_price=Decimal(str(plan.base_price)),
            age=data.age,
            age_ranges=age_ranges,
            country_override=country_override,
            quantity=data.quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return PriceCalculationResponse(
        plan_id=plan.id,
        plan_name=plan.name,
        base_price=calc_result["base_price"],
        country_override=calc_result["country_override"],
        age_surcharge_percentage=calc_result["age_surcharge_percentage"],
        age_surcharge_amount=calc_result["age_surcharge_amount"],
        final_price=calc_result["final_price"],
        currency=plan.currency,
        breakdown=calc_result
    )
