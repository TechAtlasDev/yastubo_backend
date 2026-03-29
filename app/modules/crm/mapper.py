from app.modules.emission.state_machine import PolicyStatus


def policy_status_to_zoho_stage(status: PolicyStatus | str) -> str:
    status_value = status.value if isinstance(status, PolicyStatus) else str(status)
    mapping = {
        PolicyStatus.DRAFT.value: "Qualification",
        PolicyStatus.PENDING_PAYMENT.value: "Needs Analysis",
        PolicyStatus.ACTIVE.value: "Closed Won",
        PolicyStatus.IN_ARREARS.value: "Value Proposition",
        PolicyStatus.CANCELLED.value: "Closed Lost",
        PolicyStatus.CASE_REPORTED.value: "Value Proposition",
        PolicyStatus.CASE_CLOSED.value: "Closed Won",
    }
    return mapping.get(status_value, "Qualification")


def client_to_zoho_contact(client) -> dict:
    data = {
        "First_Name": client.first_name,
        "Last_Name": client.last_name,
        "Email": client.email,
        "Phone": client.phone,
        "Mailing_Country": client.country_of_residence,
        "Description": f"Doc: {client.document_type} {client.document_number}",
    }
    if getattr(client, "acquisition_channel", None):
        data["Lead_Source"] = client.acquisition_channel
    if getattr(client, "campaign_name", None):
        data["Campaign_Name"] = client.campaign_name
    if getattr(client, "churn_risk_level", None):
        data["Churn_Risk_Level"] = client.churn_risk_level
    if getattr(client, "collections_risk_level", None):
        data["Collections_Risk_Level"] = client.collections_risk_level
    if getattr(client, "last_failed_payment_at", None):
        data["Last_Failed_Payment"] = client.last_failed_payment_at.isoformat()
    if getattr(client, "chatwoot_contact_id", None):
        data["Chatwoot_ID"] = client.chatwoot_contact_id
    return data


def policy_to_zoho_deal(policy, plan_name: str, beneficiaries=None) -> dict:
    data = {
        "Deal_Name": f"Póliza {policy.policy_number}",
        "Amount": float(policy.final_price),
        "Stage": policy_status_to_zoho_stage(policy.status),
        "Closing_Date": policy.end_date.isoformat() if policy.end_date else None,
        "Description": f"Plan: {plan_name} | País: {policy.country_code}",
        "Currency": getattr(policy, "currency", "USD"),
        "Beneficiaries_Count": len(beneficiaries) if beneficiaries else 0,
    }
    if beneficiaries:
        active = [b for b in beneficiaries if not getattr(b, "deceased_flag", False)]
        data["Active_Beneficiaries"] = len(active)
    return data


def lead_to_zoho_lead(lead) -> dict:
    data = {
        "First_Name": lead.first_name or "",
        "Last_Name": lead.last_name or "Unknown",
        "Phone": lead.phone_e164,
        "Email": lead.email or "",
        "Lead_Status": lead.lead_status if isinstance(lead.lead_status, str) else lead.lead_status.value,
        "Lead_Source": lead.source_channel or "",
        "Country": lead.country_of_residence or "",
        "Description": f"Funnel: {lead.funnel_stage} | Score: {lead.lead_score}",
    }
    if getattr(lead, "campaign_name", None):
        data["Campaign_Name"] = lead.campaign_name
    if getattr(lead, "utm_source", None):
        data["UTM_Source"] = lead.utm_source
    if getattr(lead, "utm_medium", None):
        data["UTM_Medium"] = lead.utm_medium
    if getattr(lead, "utm_campaign", None):
        data["UTM_Campaign"] = lead.utm_campaign
    return data


def beneficiary_to_zoho_contact(beneficiary, policy_number: str) -> dict:
    return {
        "First_Name": beneficiary.first_name,
        "Last_Name": beneficiary.last_name,
        "Phone": "",
        "Mailing_Country": beneficiary.country_of_residence,
        "Description": (
            f"Beneficiary of policy {policy_number} | "
            f"Kinship: {beneficiary.kinship_type} | "
            f"Status: {beneficiary.coverage_status} | "
            f"Deceased: {beneficiary.deceased_flag}"
        ),
    }
