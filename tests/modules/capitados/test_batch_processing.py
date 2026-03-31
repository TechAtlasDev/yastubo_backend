import pytest
import io
import uuid
import asyncio
from openpyxl import Workbook
from httpx import AsyncClient
from sqlalchemy import select
from app.modules.capitados.models import CapitadosMonthlyRecord
from app.modules.geography.models import Country
from app.modules.auth.security import create_access_token


@pytest.fixture
async def setup_geography(db_session):
    # Add Colombia and Mexico
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


def create_excel_file(rows: list):
    wb = Workbook()
    ws = wb.active
    # Common headers
    ws.append(
        [
            "documento",
            "nombre",
            "sexo",
            "pais_residencia",
            "pais_repatriacion",
            "edad",
            "producto_id",
            "version_id",
        ]
    )
    for row in rows:
        ws.append(row)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


@pytest.mark.asyncio
async def test_batch_upload_and_processing_mixed(
    client: AsyncClient,
    admin_user,
    default_company,
    created_product,
    setup_geography,
    db_session,
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    product_id = created_product["id"]
    version_id = created_product["plans"][0]["versions"][0]["version_number"]

    # 1. Prepare Mixed Excel
    # Rows:
    # - Valid (new insured)
    # - Valid (another new insured)
    # - Duplicate (same as first)
    # - Invalid (missing document)
    # - Invalid (wrong product id)
    rows = [
        ["12345678", "Juan Pérez", "M", "CO", "CO", 30, product_id, version_id],
        ["87654321", "Maria Lopez", "F", "MX", "CO", 45, product_id, version_id],
        [
            "12345678",
            "Juan Pérez",
            "M",
            "CO",
            "CO",
            30,
            product_id,
            version_id,
        ],  # Duplicate
        [
            "",
            "Missing Doc",
            "M",
            "CO",
            "CO",
            25,
            product_id,
            version_id,
        ],  # Error: missing doc
        [
            "99999999",
            "Wrong Prod",
            "F",
            "MX",
            "MX",
            40,
            str(uuid.uuid4()),
            version_id,
        ],  # Error: product not found
    ]
    excel_data = create_excel_file(rows)

    # 2. Upload
    payload = {"company_id": str(default_company.id), "coverage_month": "2026-04-01"}
    files = {
        "file": (
            "test_batch.xlsx",
            excel_data,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    response = await client.post(
        "/api/v1/capitados/batches/upload", data=payload, files=files, headers=headers
    )
    assert response.status_code == 200
    batch_data = response.json()
    batch_id = batch_data["id"]

    # 3. Wait for background task (since we are in tests, we might need to wait or use a sync wrapper)
    # In FastAPI tests with BackgroundTasks, we can sometimes just wait a bit if it's truly async
    # OR if using the test client correctly it might run synchronously.
    # Let's poll for a few seconds.
    max_retries = 10
    while max_retries > 0:
        res = await client.get(f"/api/v1/capitados/batches/{batch_id}", headers=headers)
        if res.json()["status"] == "completed":
            batch_data = res.json()
            break
        await asyncio.sleep(0.5)
        max_retries -= 1

    assert batch_data["status"] == "completed"
    assert batch_data["total_rows"] == 5
    assert batch_data["total_applied"] == 2
    assert batch_data["total_duplicated"] == 1
    assert batch_data["total_rejected"] == 2
    assert batch_data["reconciliation_status"] == "con_diferencias"

    # 4. Verify Database state
    # Records applied
    res = await db_session.execute(
        select(CapitadosMonthlyRecord).where(
            CapitadosMonthlyRecord.load_batch_id == uuid.UUID(batch_id)
        )
    )
    records = res.scalars().all()
    assert len(records) == 2

    # Verify pricing (Maria Lopez, 45 years old, MX residence)
    # Maria is 45 -> 20% surcharge in created_product fixture
    # Base price for CO is 50.00
    # MX has price override of 60.00 in fixture
    # Maria: Base 60.00 + 20% surcharge (12.00) = 72.00
    maria = next(r for r in records if r.full_name == "Maria Lopez")
    assert float(maria.price_base) == 60.00
    assert float(maria.age_surcharge_percent) == 20.0
    assert float(maria.price_final) == 72.00

    # Juan: Base 50.00 (CO) + 0% surcharge (30 years old) = 50.00
    juan = next(r for r in records if r.full_name == "Juan Pérez")
    assert float(juan.price_base) == 50.00
    assert float(juan.age_surcharge_percent) == 0.0
    assert float(juan.price_final) == 50.00


@pytest.mark.asyncio
async def test_batch_re_upload_all_duplicates(
    client: AsyncClient,
    admin_user,
    default_company,
    created_product,
    setup_geography,
    db_session,
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    product_id = created_product["id"]
    version_id = created_product["plans"][0]["versions"][0]["version_number"]

    rows = [
        ["11111111", "Dup 1", "M", "CO", "CO", 20, product_id, version_id],
    ]
    excel_data = create_excel_file(rows)

    payload = {"company_id": str(default_company.id), "coverage_month": "2026-05-01"}

    # First upload
    res1 = await client.post(
        "/api/v1/capitados/batches/upload",
        data=payload,
        files={"file": ("f1.xlsx", excel_data)},
        headers=headers,
    )
    b1_id = res1.json()["id"]

    # Wait
    for _ in range(10):
        r = await client.get(f"/api/v1/capitados/batches/{b1_id}", headers=headers)
        if r.json()["status"] == "completed":
            break
        await asyncio.sleep(0.2)

    # Second upload same file same month
    res2 = await client.post(
        "/api/v1/capitados/batches/upload",
        data=payload,
        files={"file": ("f2.xlsx", excel_data)},
        headers=headers,
    )
    b2_id = res2.json()["id"]

    # Wait
    for _ in range(10):
        r = await client.get(f"/api/v1/capitados/batches/{b2_id}", headers=headers)
        if r.json()["status"] == "completed":
            b2_data = r.json()
            break
        await asyncio.sleep(0.2)

    assert b2_data["total_applied"] == 0
    assert b2_data["total_duplicated"] == 1
    assert (
        b2_data["reconciliation_status"] == "conciliado"
    )  # Duplicates are not "errors" per requirement


@pytest.mark.asyncio
async def test_batch_invalid_file_extension(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"company_id": str(uuid.uuid4()), "coverage_month": "2026-04-01"}
    files = {"file": ("test.txt", b"not an excel", "text/plain")}

    response = await client.post(
        "/api/v1/capitados/batches/upload", data=payload, files=files, headers=headers
    )
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]
