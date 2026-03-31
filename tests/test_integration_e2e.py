import pytest
import uuid
import io
import asyncio
from httpx import AsyncClient
from openpyxl import Workbook
from sqlalchemy import select

from app.modules.auth.security import create_access_token
from app.modules.capitados.models import CapitadosMonthlyRecord
from app.modules.finance.models import Currency


@pytest.fixture
async def setup_currencies(db_session):
    usd = await db_session.get(Currency, "USD")
    if not usd:
        usd = Currency(code="USD", name="US Dollar", symbol="$")
        db_session.add(usd)
        await db_session.commit()
    return usd


@pytest.fixture
async def setup_geography_e2e(db_session):
    from app.modules.geography.models import Country

    countries = [
        {
            "id": 1,
            "iso2": "CO",
            "iso3": "COL",
            "name": {"es": "Colombia"},
            "continent_code": "SA",
        },
        {
            "id": 2,
            "iso2": "MX",
            "iso3": "MEX",
            "name": {"es": "México"},
            "continent_code": "NA",
        },
    ]
    for cdata in countries:
        res = await db_session.execute(
            select(Country).where(Country.iso2 == cdata["iso2"])
        )
        if not res.scalar_one_or_none():
            c = Country(**cdata)
            db_session.add(c)
    await db_session.commit()


def create_excel_e2e(rows: list):
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
            "document_number",
            "full_name",
            "sex",
            "residence",
            "repatriation",
            "age",
            "product_id",
        ]
    )
    for row in rows:
        ws.append(row)
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


@pytest.mark.asyncio
async def test_e2e_migration_flow(
    client: AsyncClient,
    admin_user,
    default_company,
    setup_currencies,
    setup_geography_e2e,
    db_session,
):
    """
    E2E Flow:
    1. Create Product -> Plan -> PlanVersion
    2. Upload Capitados Batch
    3. Verify Records & Pricing
    """
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Product System via API
    product_payload = {
        "name": "E2E Corporate Product",
        "description": "Product for integration testing",
        "product_type": "repatriation",
        "is_active": True,
        "plans": [
            {
                "name": "Standard Plan",
                "description": "Base plan",
                "is_active": True,
                "versions": [
                    {
                        "version_number": 1,
                        "cost_price": 10.00,
                        "public_price": 20.00,
                        "currency": "USD",
                        "max_entry_age": 70,
                        "max_renewal_age": 90,
                        "wtime_suicide": 365,
                        "wtime_preexisting": 180,
                        "wtime_accident": 0,
                        "age_surcharges": [
                            {"min_age": 60, "max_age": 70, "surcharge_percentage": 50.0}
                        ],
                        "countries": [
                            {
                                "country_code": "MX",
                                "country_name": "Mexico",
                                "price_override": 25.0,
                                "is_available": True,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    prod_res = await client.post(
        "/api/v1/products/", json=product_payload, headers=headers
    )
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 2. Upload Batch
    # Insured 1: CO (Base price 20), Age 30 (No surcharge) -> 20.00
    # Insured 2: MX (Override 25), Age 65 (50% surcharge) -> 25 + 12.5 = 37.50
    rows = [
        ["E2E-001", "John Doe", "M", "CO", "CO", 30, product_id],
        ["E2E-002", "Jane Smith", "F", "MX", "CO", 65, product_id],
    ]
    excel_content = create_excel_e2e(rows)

    batch_payload = {
        "company_id": str(default_company.id),
        "coverage_month": "2026-06-01",
    }
    files = {"file": ("e2e_test.xlsx", excel_content)}

    upload_res = await client.post(
        "/api/v1/capitados/batches/upload",
        data=batch_payload,
        files=files,
        headers=headers,
    )
    assert upload_res.status_code == 200
    batch_id = upload_res.json()["id"]

    # Wait for processing
    for _ in range(20):
        status_res = await client.get(
            f"/api/v1/capitados/batches/{batch_id}", headers=headers
        )
        if status_res.json()["status"] == "completed":
            break
        await asyncio.sleep(0.5)

    assert status_res.json()["status"] == "completed"
    assert status_res.json()["total_applied"] == 2

    # 3. Verify Final Records in DB
    records_res = await db_session.execute(
        select(CapitadosMonthlyRecord).where(
            CapitadosMonthlyRecord.load_batch_id == uuid.UUID(batch_id)
        )
    )
    records = records_res.scalars().all()
    assert len(records) == 2

    john = next(r for r in records if r.full_name == "John Doe")
    assert float(john.price_final) == 20.00

    jane = next(r for r in records if r.full_name == "Jane Smith")
    assert float(jane.price_final) == 37.50
