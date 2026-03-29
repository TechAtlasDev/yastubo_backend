import asyncio
import pandas as pd
from io import BytesIO
import uuid
from datetime import datetime, timedelta, date
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.emission.models import Client, Policy, PolicyStatusHistory, Beneficiary
from app.modules.emission.schemas import (
    ClientCreate,
    EmissionRequest,
    StatusTransitionRequest,
    BeneficiaryCreate,
    BulkEmissionRequest,
    BulkEmissionResponse,
)
from app.modules.emission import state_machine, pdf_generator
from app.modules.plans import service as plans_service
from app.modules.plans import calculator
from app.modules.notifications.service import get_notifications_service
from app.modules.crm.service import sync_policy_to_crm, update_policy_stage_in_crm, sync_beneficiary_to_crm
from app.modules.crm.zoho_client import get_zoho_client
from app.modules.audit.decorator import audited
from app.core.events import dispatch_event_background


@audited(action="CLIENT_REGISTERED", entity="Client")
async def register_client(
    db: AsyncSession,
    data: ClientCreate,
    created_by: uuid.UUID,
    workspace_id: Optional[uuid.UUID] = None,
) -> Client:
    # Check if email exists
    existing = await db.execute(select(Client).where(Client.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this email already exists",
        )

    if workspace_id is None:
        # Resolve workspace from user
        from app.modules.workspaces.models import UserWorkspace

        res = await db.execute(
            select(UserWorkspace.workspace_id)
            .where(UserWorkspace.user_id == created_by)
            .limit(1)
        )
        workspace_id = res.scalar_one_or_none()
        if not workspace_id:
            raise HTTPException(
                status_code=400, detail="User has no associated workspace."
            )

    client = Client(
        **data.model_dump(), created_by=created_by, workspace_id=workspace_id
    )
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


def calculate_age(birth_date: date, reference_date: date) -> int:
    return (
        reference_date.year
        - birth_date.year
        - (
            (reference_date.month, reference_date.day)
            < (birth_date.month, birth_date.day)
        )
    )


@audited(action="POLICY_ISSUED", entity="Policy")
async def issue_policy(
    db: AsyncSession, data: EmissionRequest, issued_by: uuid.UUID
) -> Policy:
    # 1. Get Client
    client = await get_client(db, data.client_id)

    # NEW PHASE 2: Check or create lead for abandonment tracking
    from app.modules.leads import service as leads_service
    from app.modules.leads.schemas import LeadCreate

    lead = await leads_service.create_or_update_lead(
        db,
        LeadCreate(
            workspace_id=client.workspace_id,
            phone_e164=client.phone,
            first_name=client.first_name,
            last_name=client.last_name,
            email=client.email,
            country_of_residence=client.country_of_residence,
            nationality=client.nationality,
            # Pass marketing attribution if available in client (from registration)
            acquisition_channel=client.acquisition_channel,
            campaign_name=client.campaign_name,
        ),
    )
    # Update lead status to intent
    from app.modules.leads.schemas import LeadUpdate

    await leads_service.update_lead(db, lead.id, LeadUpdate(checkout_started=True))

    # 2. Get Plan
    plan = await plans_service.get_plan(db, data.plan_id)
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Plan is inactive")

    # 3. Handle Beneficiaries (Default to client if empty)
    beneficiaries_data = data.beneficiaries
    if not beneficiaries_data:
        beneficiaries_data = [
            BeneficiaryCreate(
                first_name=client.first_name,
                last_name=client.last_name,
                date_of_birth=client.birth_date,
                kinship_type="SELF",
                country_of_residence=client.country_of_residence,
            )
        ]

    config = next(
        (
            cc
            for cc in plan.country_configs
            if cc.country_code == data.country_code and cc.is_available
        ),
        None,
    )
    if not config:
        raise HTTPException(
            status_code=422, detail=f"Plan not available in country {data.country_code}"
        )

    # 4. Process each beneficiary
    age_ranges = [
        {
            "min_age": ar.min_age,
            "max_age": ar.max_age,
            "surcharge_percentage": ar.surcharge_percentage,
        }
        for ar in plan.age_ranges
    ]
    country_override = (
        Decimal(str(config.base_price_override))
        if config.base_price_override is not None
        else None
    )

    total_base_price = Decimal("0.00")
    total_surcharge = Decimal("0.00")
    total_final_price = Decimal("0.00")

    beneficiaries_to_create = []

    for b_data in beneficiaries_data:
        age = calculate_age(b_data.date_of_birth, data.start_date)

        # Validate eligibility
        if age > plan.max_entry_age:
            raise HTTPException(
                status_code=422,
                detail=f"Beneficiary {b_data.first_name} age {age} exceeds max entry age {plan.max_entry_age}",
            )

        try:
            calc_result = calculator.calculate_price(
                base_price=Decimal(str(plan.base_price)),
                age=age,
                age_ranges=age_ranges,
                country_override=country_override,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Error calculating price for {b_data.first_name}: {str(e)}",
            )

        beneficiary = Beneficiary(
            first_name=b_data.first_name,
            last_name=b_data.last_name,
            date_of_birth=b_data.date_of_birth,
            kinship_type=b_data.kinship_type,
            country_of_residence=b_data.country_of_residence,
            location_type=b_data.location_type,
            individual_price=float(calc_result["final_price"]),
            # Beneficiary doesn't have workspace_id, it's linked to Policy
        )
        beneficiaries_to_create.append(beneficiary)

        total_base_price += calc_result["base_price"]
        total_surcharge += calc_result["age_surcharge_amount"]
        total_final_price += calc_result["final_price"]

    # 5. Generate policy number
    year = datetime.now().year
    count_res = await db.execute(select(func.count(Policy.id)))
    counter = count_res.scalar() + 1
    policy_number = f"YAS-{year}-{counter:06d}"

    # 6. Snapshot
    plan_snapshot = {
        "name": plan.name,
        "base_price": float(plan.base_price),
        "age_ranges": [
            {
                "min": ar.min_age,
                "max": ar.max_age,
                "pct": float(ar.surcharge_percentage),
            }
            for ar in plan.age_ranges
        ],
        "countries": [
            {
                "code": cc.country_code,
                "price": float(cc.base_price_override)
                if cc.base_price_override is not None
                else None,
            }
            for cc in plan.country_configs
        ],
        "coverages": [c.name for c in plan.coverages],
        "terms_es": plan.terms_es,
        "repatriation_countries": plan.repatriation_countries,
    }

    # 7. Create Policy (DRAFT)
    end_date = data.start_date + timedelta(days=365)  # 1 year by default
    ws_id = client.workspace_id
    if not ws_id:
        from app.modules.workspaces.models import Workspace

        res_ws = await db.execute(select(Workspace.id).limit(1))
        ws_id = res_ws.scalar_one_or_none()
        if not ws_id:
            raise HTTPException(
                status_code=500,
                detail="Serious integrity error: No workspace found in system.",
            )

    policy = Policy(
        workspace_id=ws_id,
        policy_number=policy_number,
        client_id=client.id,
        lead_id=lead.id,  # Link lead for Phase 2
        plan_id=plan.id,
        plan_version_snapshot=plan_snapshot,
        status=state_machine.PolicyStatus.DRAFT,
        base_price=float(total_base_price),
        surcharge_amount=float(total_surcharge),
        final_price=float(total_final_price),
        currency=plan.currency,
        country_code=data.country_code,
        start_date=data.start_date,
        end_date=end_date,
        notes=data.notes,
        issued_by=issued_by,
        issued_at=datetime.now(),
    )

    # Link beneficiaries
    for b in beneficiaries_to_create:
        b.policy = policy
        db.add(b)

    db.add(policy)
    await db.flush()

    # 8. History (INITIAL -> DRAFT)
    h1 = PolicyStatusHistory(
        policy_id=policy.id,
        from_status=None,
        to_status=state_machine.PolicyStatus.DRAFT,
        changed_by=issued_by,
        reason="Policy creation",
    )
    db.add(h1)

    # 9. Transition to PENDING_PAYMENT
    old_status = policy.status
    new_status = state_machine.transition(
        old_status, state_machine.PolicyStatus.PENDING_PAYMENT
    )
    policy.status = new_status

    # 10. History (DRAFT -> PENDING_PAYMENT)
    h2 = PolicyStatusHistory(
        policy_id=policy.id,
        from_status=old_status,
        to_status=new_status,
        changed_by=issued_by,
        reason="Auto-transition to pending payment",
    )
    db.add(h2)

    # 11. Generate PDF
    pdf_bytes = pdf_generator.generate_contract_pdf(policy, client, plan_snapshot)

    # 12. Save path
    policy.pdf_path = f"storage/policies/{policy_number}.pdf"

    # 13. Notifications
    notifications = get_notifications_service()
    await notifications.on_policy_issued(policy, client, pdf_bytes)

    await db.commit()

    # 14. CRM sync (best-effort, non-blocking)
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
            selectinload(Policy.beneficiaries),
            selectinload(Policy.status_history),
        )
    )
    policy = res.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


async def list_policies(
    db: AsyncSession,
    status: Optional[str] = None,
    client_id: Optional[uuid.UUID] = None,
) -> List[Policy]:
    query = select(Policy).options(
        selectinload(Policy.client),
        selectinload(Policy.beneficiaries),
        selectinload(Policy.status_history),
    )
    if status:
        query = query.where(Policy.status == status)
    if client_id:
        query = query.where(Policy.client_id == client_id)

    res = await db.execute(query)
    return list(res.scalars().all())


@audited(action="POLICY_STATUS_CHANGED", entity="Policy")
async def change_policy_status(
    db: AsyncSession,
    policy_id: uuid.UUID,
    data: StatusTransitionRequest,
    changed_by: uuid.UUID,
) -> Policy:
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
        reason=data.reason,
    )
    db.add(history)

    await db.commit()
    await db.refresh(policy, ["status_history", "beneficiaries"])

    # Best-effort, non-blocking CRM stage update
    asyncio.create_task(update_policy_stage_in_crm(get_zoho_client(), policy))

    return policy


async def get_beneficiary(db: AsyncSession, beneficiary_id: uuid.UUID) -> Beneficiary:
    res = await db.execute(
        select(Beneficiary)
        .where(Beneficiary.id == beneficiary_id)
        .options(selectinload(Beneficiary.policy))
    )
    beneficiary = res.scalar_one_or_none()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return beneficiary


@audited(action="BENEFICIARY_MARKED_DECEASED", entity="Beneficiary")
async def mark_beneficiary_deceased(
    db: AsyncSession, beneficiary_id: uuid.UUID, reported_by: str
) -> Beneficiary:
    from app.modules.payments.models import Subscription
    from app.modules.payments.stripe_client import get_stripe_client

    beneficiary = await get_beneficiary(db, beneficiary_id)

    if beneficiary.deceased_flag:
        return beneficiary

    beneficiary.deceased_flag = True
    beneficiary.deceased_reported_at = datetime.now()
    beneficiary.deceased_reported_by = reported_by
    beneficiary.coverage_status = "DECEASED"

    # Adjust the Stripe subscription to exclude the deceased beneficiary's price
    policy = beneficiary.policy
    new_price = float(policy.final_price) - float(beneficiary.individual_price)
    new_price_cents = max(0, int(round(new_price * 100)))

    sub_res = await db.execute(
        select(Subscription).where(Subscription.policy_id == policy.id)
    )
    subscription = sub_res.scalar_one_or_none()

    if subscription and new_price_cents > 0:
        try:
            stripe_client = get_stripe_client()
            await stripe_client.update_subscription_item_price(
                subscription_id=subscription.stripe_subscription_id,
                new_amount_cents=new_price_cents,
                currency=policy.currency.lower(),
            )
            # Update local snapshot
            subscription.monthly_price = new_price
            subscription.mrr_snapshot = new_price
            beneficiary.billing_adjustment_confirmed = True
        except Exception as exc:
            from loguru import logger
            logger.error(
                "[BILLING_ADJUSTMENT] Failed to update Stripe subscription for policy={} beneficiary={}: {}",
                policy.policy_number,
                beneficiary_id,
                exc,
            )
            # billing_adjustment_confirmed stays False until manually resolved
    elif subscription and new_price_cents == 0:
        # All beneficiaries deceased — cancel subscription
        try:
            stripe_client = get_stripe_client()
            await stripe_client.cancel_subscription(
                subscription.stripe_subscription_id, at_period_end=True
            )
            beneficiary.billing_adjustment_confirmed = True
        except Exception as exc:
            from loguru import logger
            logger.error(
                "[BILLING_ADJUSTMENT] Failed to cancel Stripe subscription for policy={}: {}",
                policy.policy_number,
                exc,
            )

    # Update policy final_price to reflect the removal
    policy.final_price = new_price

    await db.commit()
    await db.refresh(beneficiary)

    dispatch_event_background(
        "BENEFICIARY_DECEASED",
        {
            "beneficiary_id": str(beneficiary.id),
            "policy_number": beneficiary.policy.policy_number,
            "reported_by": reported_by,
        },
    )

    # Sync updated beneficiary status to Zoho CRM (best-effort)
    asyncio.create_task(
        sync_beneficiary_to_crm(
            get_zoho_client(), beneficiary, beneficiary.policy.policy_number
        )
    )

    return beneficiary


async def bulk_issue_policy(
    db: AsyncSession,
    data: BulkEmissionRequest,
    file_content: bytes,
    issued_by: uuid.UUID,
) -> BulkEmissionResponse:
    # 1. Read Excel
    try:
        df = pd.read_excel(BytesIO(file_content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")

    # 2. Map to BeneficiaryCreate
    beneficiaries = []
    errors = []

    # Required columns
    required = [
        "first_name",
        "last_name",
        "date_of_birth",
        "kinship_type",
        "country_of_residence",
    ]
    for col in required:
        if col not in df.columns:
            raise HTTPException(
                status_code=400, detail=f"Missing required column in Excel: {col}"
            )

    for index, row in df.iterrows():
        try:
            # Basic validation/cleaning
            dob = row["date_of_birth"]
            if isinstance(dob, str):
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            elif isinstance(dob, (datetime, date)):
                if isinstance(dob, datetime):
                    dob = dob.date()
            else:
                # Handle potential pandas Timestamp
                dob = pd.to_datetime(dob).date()

            beneficiary = BeneficiaryCreate(
                first_name=str(row["first_name"]),
                last_name=str(row["last_name"]),
                date_of_birth=dob,
                kinship_type=str(row["kinship_type"]).upper(),
                country_of_residence=str(row["country_of_residence"]).upper(),
                location_type=str(row.get("location_type", "URBAN")).upper(),
            )
            beneficiaries.append(beneficiary)
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")

    if not beneficiaries:
        raise HTTPException(
            status_code=400, detail="No valid beneficiaries found in the file."
        )

    # 3. Call standard issue_policy
    emission_req = EmissionRequest(
        client_id=data.client_id,
        plan_id=data.plan_id,
        country_code=data.country_code,
        start_date=data.start_date,
        notes=data.notes,
        beneficiaries=beneficiaries,
    )

    policy = await issue_policy(db, emission_req, issued_by)

    return BulkEmissionResponse(
        policy_id=policy.id,
        policy_number=policy.policy_number,
        beneficiaries_count=len(policy.beneficiaries),
        errors=errors,
        message=f"Successfully issued policy for {len(policy.beneficiaries)} beneficiaries.",
    )
