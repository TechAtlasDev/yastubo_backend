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
    return {
        "First_Name": client.first_name,
        "Last_Name": client.last_name,
        "Email": client.email,
        "Phone": client.phone,
        "Mailing_Country": client.country_of_residence,
        "Description": f"Doc: {client.document_type} {client.document_number}",
    }


def policy_to_zoho_deal(policy, plan_name: str) -> dict:
    return {
        "Deal_Name": f"Póliza {policy.policy_number}",
        "Amount": float(policy.final_price),
        "Stage": policy_status_to_zoho_stage(policy.status),
        "Closing_Date": policy.end_date.isoformat() if policy.end_date else None,
        "Description": f"Plan: {plan_name} | País: {policy.country_code}",
    }
