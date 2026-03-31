import uuid
from decimal import Decimal
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.modules.plans.models import (
    Product,
    Plan,
    PlanVersion,
    PlanVersionAgeSurcharge,
    PlanVersionCountry,
    PlanVersionCoverage,
    PlanVersionRepatriationCountry,
)
from app.modules.plans.schemas import (
    ProductCreate,
    PriceCalculationRequest,
    PriceCalculationResponse,
)
from app.modules.plans import calculator
from app.modules.audit.decorator import audited


@audited(action="PRODUCT_CREATED", entity="Product")
async def create_product(
    db: AsyncSession, data: ProductCreate, created_by: uuid.UUID
) -> Product:
    product = Product(
        name=data.name,
        description=data.description,
        product_type=data.product_type,
        is_active=data.is_active,
    )
    db.add(product)
    await db.flush()

    for plan_data in data.plans:
        plan = Plan(
            product_id=product.id,
            company_id=plan_data.company_id,
            name=plan_data.name,
            description=plan_data.description,
            is_active=plan_data.is_active,
        )
        db.add(plan)
        await db.flush()

        for version_data in plan_data.versions:
            version = PlanVersion(
                plan_id=plan.id,
                version_number=version_data.version_number,
                cost_price=float(version_data.cost_price)
                if version_data.cost_price
                else None,
                public_price=float(version_data.public_price)
                if version_data.public_price
                else None,
                currency=version_data.currency,
                max_entry_age=version_data.max_entry_age,
                max_renewal_age=version_data.max_renewal_age,
                wtime_suicide=version_data.wtime_suicide,
                wtime_preexisting=version_data.wtime_preexisting,
                wtime_accident=version_data.wtime_accident,
                terms_es=version_data.terms_es,
                terms_en=version_data.terms_en,
                is_active=version_data.is_active,
                created_by=created_by,
            )
            db.add(version)
            await db.flush()

            for ar in version_data.age_surcharges:
                db.add(
                    PlanVersionAgeSurcharge(
                        plan_version_id=version.id,
                        min_age=ar.min_age,
                        max_age=ar.max_age,
                        surcharge_percentage=float(ar.surcharge_percentage),
                    )
                )

            for cc in version_data.countries:
                db.add(
                    PlanVersionCountry(
                        plan_version_id=version.id,
                        country_code=cc.country_code,
                        country_name=cc.country_name,
                        price_override=float(cc.price_override)
                        if cc.price_override
                        else None,
                        is_available=cc.is_available,
                    )
                )

            for cov in version_data.coverages:
                db.add(
                    PlanVersionCoverage(
                        plan_version_id=version.id,
                        coverage_id=cov.coverage_id,
                        value_int=cov.value_int,
                        value_decimal=float(cov.value_decimal)
                        if cov.value_decimal
                        else None,
                        value_text=cov.value_text,
                        notes=cov.notes,
                        is_included=cov.is_included,
                    )
                )

            for rc in version_data.repatriation_countries:
                db.add(
                    PlanVersionRepatriationCountry(
                        plan_version_id=version.id,
                        country_code=rc.country_code,
                        country_name=rc.country_name,
                    )
                )

            await db.flush()

    await db.commit()

    # Reload full tree
    await db.refresh(product)

    result = await db.execute(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.age_surcharges),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.countries),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.coverages)
            .selectinload(PlanVersionCoverage.coverage),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.repatriation_countries),
        )
    )
    return result.scalar_one()


async def list_products(db: AsyncSession, active_only: bool = True) -> List[Product]:
    query = select(Product).options(
        selectinload(Product.plans)
        .selectinload(Plan.versions)
        .selectinload(PlanVersion.age_surcharges),
        selectinload(Product.plans)
        .selectinload(Plan.versions)
        .selectinload(PlanVersion.countries),
        selectinload(Product.plans)
        .selectinload(Plan.versions)
        .selectinload(PlanVersion.coverages)
        .selectinload(PlanVersionCoverage.coverage),
        selectinload(Product.plans)
        .selectinload(Plan.versions)
        .selectinload(PlanVersion.repatriation_countries),
    )
    if active_only:
        query = query.where(Product.is_active)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Product:
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.age_surcharges),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.countries),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.coverages)
            .selectinload(PlanVersionCoverage.coverage),
            selectinload(Product.plans)
            .selectinload(Plan.versions)
            .selectinload(PlanVersion.repatriation_countries),
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def get_plan_version(db: AsyncSession, plan_version_id: uuid.UUID) -> PlanVersion:
    from sqlalchemy.orm import selectinload
    from app.modules.plans.models import (
        PlanVersionCoverage,
    )  # Need this for nested selectinload if not imported

    result = await db.execute(
        select(PlanVersion)
        .where(PlanVersion.id == plan_version_id)
        .options(
            selectinload(PlanVersion.plan),
            selectinload(PlanVersion.age_surcharges),
            selectinload(PlanVersion.countries),
            selectinload(PlanVersion.repatriation_countries),
            selectinload(PlanVersion.coverages).selectinload(
                PlanVersionCoverage.coverage
            ),
        )
    )
    pv = result.scalar_one_or_none()
    if not pv:
        raise HTTPException(status_code=404, detail="Plan version not found")
    return pv


async def get_price(
    db: AsyncSession, data: PriceCalculationRequest
) -> PriceCalculationResponse:
    pv = await get_plan_version(db, data.plan_version_id)
    if not pv.is_active:
        raise HTTPException(status_code=400, detail="Plan Version is not active")

    # Validate country
    config = next(
        (cc for cc in pv.countries if cc.country_code == data.country_code),
        None,
    )
    if not config or not config.is_available:
        raise HTTPException(
            status_code=422, detail=f"Plan not available in country {data.country_code}"
        )

    # Validate age
    if pv.max_entry_age and data.age > pv.max_entry_age:
        raise HTTPException(
            status_code=422,
            detail=f"Age {data.age} exceeds max entry age {pv.max_entry_age}",
        )

    # Prepare for calculator
    age_ranges = [
        {
            "min_age": ar.min_age,
            "max_age": ar.max_age,
            "surcharge_percentage": ar.surcharge_percentage,
        }
        for ar in pv.age_surcharges
    ]
    country_override = (
        Decimal(str(config.price_override))
        if config.price_override is not None
        else None
    )

    base_price = Decimal(str(pv.public_price)) if pv.public_price else Decimal("0.0")

    try:
        calc_result = calculator.calculate_price(
            base_price=base_price,
            age=data.age,
            age_ranges=age_ranges,
            country_override=country_override,
            quantity=data.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return PriceCalculationResponse(
        plan_version_id=pv.id,
        plan_name=pv.plan.name,
        base_price=calc_result["base_price"],
        country_override=calc_result["country_override"],
        age_surcharge_percentage=calc_result["age_surcharge_percentage"],
        age_surcharge_amount=calc_result["age_surcharge_amount"],
        final_price=calc_result["final_price"],
        currency=pv.currency,
        breakdown=calc_result,
    )
