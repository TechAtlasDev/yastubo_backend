from loguru import logger

from app.modules.crm.mapper import (
    client_to_zoho_contact,
    policy_status_to_zoho_stage,
    policy_to_zoho_deal,
)


async def sync_client_to_crm(zoho, client) -> str | None:
    try:
        payload = client_to_zoho_contact(client)
        contact_id = await zoho.create_or_update_contact(payload)
        logger.info(
            "[CRM] sync_client email={} contact_id={}", client.email, contact_id
        )
        return contact_id
    except Exception as exc:
        logger.error("[CRM] sync_client_to_crm error={}", exc)
        return None


async def sync_policy_to_crm(zoho, policy, client, plan_name: str) -> str | None:
    try:
        contact_id = await sync_client_to_crm(zoho, client)
        if not contact_id:
            return None

        deal_payload = policy_to_zoho_deal(policy, plan_name)
        deal_id = await zoho.create_or_update_deal(deal_payload, contact_id)
        logger.info(
            "[CRM] sync_policy policy={} deal_id={}", policy.policy_number, deal_id
        )
        return deal_id
    except Exception as exc:
        logger.error("[CRM] sync_policy_to_crm error={}", exc)
        return None


async def update_policy_stage_in_crm(zoho, policy) -> bool:
    try:
        deal_id = getattr(policy, "crm_deal_id", None)
        if not deal_id:
            logger.info(
                "[CRM] no deal_id for policy={}, skipping stage update",
                policy.policy_number,
            )
            return False
        stage = policy_status_to_zoho_stage(policy.status)
        ok = await zoho.update_deal_stage(deal_id=deal_id, stage=stage)
        logger.info(
            "[CRM] update_stage policy={} stage={} ok={}",
            policy.policy_number,
            stage,
            ok,
        )
        return ok
    except Exception as exc:
        logger.error("[CRM] update_policy_stage_in_crm error={}", exc)
        return False
