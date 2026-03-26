
import pytest

from app.modules.crm.mapper import policy_status_to_zoho_stage
from app.modules.crm.zoho_client import ZohoClient
from app.modules.emission.state_machine import PolicyStatus


@pytest.mark.asyncio
async def test_zoho_gets_access_token_and_caches_it(mock_httpx):
    mock_httpx.enqueue(
        mock_httpx.response(status_code=200, json_data={"access_token": "token-1", "expires_in": 3600}),
        mock_httpx.response(status_code=200, json_data={"data": [{"details": {"id": "contact-1"}}]}),
        mock_httpx.response(status_code=200, json_data={"data": [{"details": {"id": "contact-2"}}]}),
    )

    zoho = ZohoClient("id", "secret", "refresh", "https://www.zohoapis.com/crm/v3", enabled=True)

    first = await zoho.create_or_update_contact({"Email": "a@example.com"})
    second = await zoho.create_or_update_contact({"Email": "b@example.com"})

    assert first == "contact-1"
    assert second == "contact-2"
    token_calls = [c for c in mock_httpx.calls if "oauth/v2/token" in c[1]]
    assert len(token_calls) == 1


@pytest.mark.asyncio
async def test_zoho_skips_all_calls_when_disabled(mock_httpx):
    zoho = ZohoClient("id", "secret", "refresh", "https://www.zohoapis.com/crm/v3", enabled=False)

    contact = await zoho.create_or_update_contact({"Email": "a@example.com"})
    deal = await zoho.create_or_update_deal({"Deal_Name": "X"}, "contact-id")
    stage_ok = await zoho.update_deal_stage("deal-id", "Closed Won")

    assert contact == "disabled"
    assert deal == "disabled"
    assert stage_ok is True
    assert len(mock_httpx.calls) == 0


def test_zoho_mapper_maps_policy_status_correctly():
    assert policy_status_to_zoho_stage(PolicyStatus.DRAFT) == "Qualification"
    assert policy_status_to_zoho_stage(PolicyStatus.PENDING_PAYMENT) == "Needs Analysis"
    assert policy_status_to_zoho_stage(PolicyStatus.ACTIVE) == "Closed Won"
    assert policy_status_to_zoho_stage(PolicyStatus.IN_ARREARS) == "Value Proposition"
    assert policy_status_to_zoho_stage(PolicyStatus.CANCELLED) == "Closed Lost"
    assert policy_status_to_zoho_stage(PolicyStatus.CASE_REPORTED) == "Value Proposition"
    assert policy_status_to_zoho_stage(PolicyStatus.CASE_CLOSED) == "Closed Won"
