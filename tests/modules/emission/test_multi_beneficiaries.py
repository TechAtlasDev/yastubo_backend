import pytest
import uuid
from httpx import AsyncClient
from datetime import date, timedelta
from app.modules.auth.security import create_access_token

@pytest.mark.asyncio
async def test_issue_policy_with_multiple_beneficiaries(client: AsyncClient, admin_user, test_client, created_plan):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Payload with 2 beneficiaries
    payload = {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "country_code": "MX",
        "start_date": str(date.today() + timedelta(days=1)),
        "notes": "Multi beneficiary test",
        "beneficiaries": [
            {
                "first_name": "Beneficiary",
                "last_name": "One",
                "date_of_birth": str(date.today() - timedelta(days=20*365)), # 20 years
                "kinship_type": "CHILD",
                "country_of_residence": "MX"
            },
            {
                "first_name": "Beneficiary",
                "last_name": "Two",
                "date_of_birth": str(date.today() - timedelta(days=50*365)), # 50 years (likely has surcharge)
                "kinship_type": "SPOUSE",
                "country_of_residence": "MX"
            }
        ]
    }
    
    from unittest.mock import patch
    with patch("app.modules.emission.pdf_generator.generate_contract_pdf", return_value=b"mock pdf"):
        response = await client.post("/api/v1/emission/issue", json=payload, headers=headers)
        
    assert response.status_code == 201
    policy = response.json()
    
    # Verify beneficiaries are created and linked
    assert len(policy["beneficiaries"]) == 2
    
    # Verify price calculation (Base is 50.00 for 20yo, and likely more for 50yo)
    # The sum should be > 100.00 if surcharge applies
    assert float(policy["final_price"]) > 100.00
    
    # Verify individual prices are stored
    for b in policy["beneficiaries"]:
        assert float(b["individual_price"]) > 0
