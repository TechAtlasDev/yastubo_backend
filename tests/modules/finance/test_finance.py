import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.finance.service import CommissionService
from app.modules.finance.models import (
    CompanyCommissionUser,
    BusinessUnitCommissionUser,
    Currency,
    UnitOfMeasure,
)
from app.modules.organizations.models import BusinessUnit


@pytest.fixture
async def seeded_finance(db_session):
    # Seed units of measure
    units = [
        {
            "id": 1,
            "name": {"en": "Sessions", "es": "Sesiones"},
            "measure_type": "integer",
        },
        {"id": 2, "name": {"en": "USD", "es": "USD"}, "measure_type": "decimal"},
    ]
    for u_data in units:
        u = UnitOfMeasure(**u_data)
        db_session.add(u)

    # Seed currency
    c = Currency(code="USD", name="United States Dollar", symbol="$")
    db_session.add(c)

    await db_session.commit()


@pytest.mark.asyncio
async def test_calculate_dispersion_happy_path(
    db_session: AsyncSession, default_company, admin_user
):
    # Setup: 10% commission for staff_user at company level
    cc = CompanyCommissionUser(
        company_id=default_company.id, user_id=admin_user.id, commission_percentage=10.0
    )
    db_session.add(cc)
    await db_session.commit()

    splits = await CommissionService.calculate_dispersion(
        db_session, 100.0, default_company.id
    )

    assert len(splits) == 1
    assert splits[0]["user_id"] == admin_user.id
    assert splits[0]["amount"] == 10.0
    assert splits[0]["level"] == "COMPANY"


@pytest.mark.asyncio
async def test_calculate_dispersion_with_bu(
    db_session: AsyncSession, default_company, admin_user
):
    # Setup: BU and another user (or same for simplicity)
    bu = BusinessUnit(company_id=default_company.id, name="Test BU", type="OFFICE")
    db_session.add(bu)
    await db_session.flush()

    # 5% Company level
    cc = CompanyCommissionUser(
        company_id=default_company.id, user_id=admin_user.id, commission_percentage=5.0
    )
    # 15% BU level
    buc = BusinessUnitCommissionUser(
        business_unit_id=bu.id, user_id=admin_user.id, commission_percentage=15.0
    )
    db_session.add_all([cc, buc])
    await db_session.commit()

    splits = await CommissionService.calculate_dispersion(
        db_session, 200.0, default_company.id, bu.id
    )

    assert len(splits) == 2
    # 5% of 200 = 10
    # 15% of 200 = 30
    amounts = [s["amount"] for s in splits]
    assert 10.0 in amounts
    assert 30.0 in amounts


@pytest.mark.asyncio
async def test_calculate_dispersion_exceeds_100_error(
    db_session: AsyncSession, default_company, admin_user
):
    cc = CompanyCommissionUser(
        company_id=default_company.id,
        user_id=admin_user.id,
        commission_percentage=110.0,
    )
    db_session.add(cc)
    await db_session.commit()

    with pytest.raises(ValueError, match="exceeds 100%"):
        await CommissionService.calculate_dispersion(
            db_session, 100.0, default_company.id
        )


@pytest.mark.asyncio
async def test_calculate_dispersion_empty_if_no_config(
    db_session: AsyncSession, default_company
):
    splits = await CommissionService.calculate_dispersion(
        db_session, 100.0, default_company.id
    )
    assert len(splits) == 0


@pytest.mark.asyncio
async def test_list_currencies_endpoint(client: AsyncClient, seeded_finance):
    res = await client.get("/api/v1/finance/currencies")
    assert res.status_code == 200
    data = res.json()
    assert any(c["code"] == "USD" for c in data)


@pytest.mark.asyncio
async def test_list_units_of_measure_endpoint(client: AsyncClient, seeded_finance):
    res = await client.get("/api/v1/finance/units-of-measure")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert any(u["id"] == 1 for u in data)


@pytest.mark.asyncio
async def test_calculate_commissions_endpoint(
    client: AsyncClient, db_session: AsyncSession, default_company, admin_user
):
    # Setup
    cc = CompanyCommissionUser(
        company_id=default_company.id, user_id=admin_user.id, commission_percentage=12.5
    )
    db_session.add(cc)
    await db_session.commit()

    payload = {"amount": 1000.0, "company_id": str(default_company.id)}
    response = await client.post("/api/v1/finance/commissions/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 125.0
    assert data[0]["percentage"] == 12.5
