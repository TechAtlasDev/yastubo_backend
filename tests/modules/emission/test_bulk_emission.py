import pytest
import io
import pandas as pd
from datetime import date, timedelta
from httpx import AsyncClient
from app.modules.auth.security import create_access_token
from unittest.mock import patch


@pytest.mark.asyncio
async def test_bulk_upload_beneficiaries_success(
    client: AsyncClient, admin_user, created_plan, test_client
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a dummy Excel file in memory
    data = {
        "first_name": ["Alice", "Bob"],
        "last_name": ["Smith", "Brown"],
        "date_of_birth": ["1990-05-15", "1985-10-20"],
        "kinship_type": ["SPOUSE", "CHILD"],
        "country_of_residence": ["MX", "MX"],
        "location_type": ["URBAN", "RURAL"],
    }
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    # 2. Prepare form data
    form_data = {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "country_code": "MX",
        "start_date": str(date.today() + timedelta(days=1)),
        "notes": "Bulk upload test",
    }

    files = {
        "file": (
            "test_beneficiaries.xlsx",
            excel_file,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    # Mock PDF generation to avoid filesystem issues
    with patch(
        "app.modules.emission.pdf_generator.generate_contract_pdf",
        return_value=b"%PDF-mock",
    ):
        response = await client.post(
            "/api/v1/emission/bulk-upload", data=form_data, files=files, headers=headers
        )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["beneficiaries_count"] == 2
    assert "Successfully issued policy" in res_data["message"]
    assert len(res_data["errors"]) == 0


@pytest.mark.asyncio
async def test_bulk_upload_missing_columns_returns_400(
    client: AsyncClient, admin_user, created_plan, test_client
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Missing 'last_name' column
    data = {
        "first_name": ["Alice"],
        "date_of_birth": ["1990-05-15"],
        "kinship_type": ["SPOUSE"],
        "country_of_residence": ["MX"],
    }
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    form_data = {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "country_code": "MX",
        "start_date": str(date.today() + timedelta(days=1)),
    }

    files = {
        "file": (
            "bad_file.xlsx",
            excel_file,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    response = await client.post(
        "/api/v1/emission/bulk-upload", data=form_data, files=files, headers=headers
    )
    assert response.status_code == 400
    assert "Missing required column" in response.json()["detail"]
