import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_country(client: AsyncClient):
    response = await client.post(
        "/api/v1/geography/countries",
        json={
            "name": {"es": "Colombia", "en": "Colombia"},
            "iso2": "CO",
            "iso3": "COL",
            "continent_code": "SA",
            "phone_code": "57",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"]["es"] == "Colombia"
    assert data["iso2"] == "CO"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_countries(client: AsyncClient, db_session: AsyncSession):
    # Add a country via service if needed, or via API
    await client.post(
        "/api/v1/geography/countries",
        json={
            "name": {"es": "España", "en": "Spain"},
            "iso2": "ES",
            "continent_code": "EU",
        },
    )

    response = await client.get("/api/v1/geography/countries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["iso2"] == "ES" for c in data)


@pytest.mark.asyncio
async def test_create_zone(client: AsyncClient):
    response = await client.post(
        "/api/v1/geography/zones",
        json={
            "name": "Latinoamérica",
            "description": "Países de habla hispana en América",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Latinoamérica"
    assert "id" in data


@pytest.mark.asyncio
async def test_associate_country_zone(client: AsyncClient, db_session: AsyncSession):
    # Create country
    rc = await client.post(
        "/api/v1/geography/countries",
        json={"name": {"es": "Chile"}, "iso2": "CL", "continent_code": "SA"},
    )
    country_id = rc.json()["id"]

    # Create zone
    rz = await client.post("/api/v1/geography/zones", json={"name": "Cono Sur"})
    zone_id = rz.json()["id"]

    # Associate
    response = await client.post(
        f"/api/v1/geography/zones/{zone_id}/countries/{country_id}"
    )
    assert response.status_code == 204

    # Verify association via get_country
    response = await client.get(f"/api/v1/geography/countries/{country_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["zones"]) == 1
    assert data["zones"][0]["name"] == "Cono Sur"

    # Verify association via get_zone
    response = await client.get(f"/api/v1/geography/zones/{zone_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["countries"]) == 1
    assert data["countries"][0]["iso2"] == "CL"
