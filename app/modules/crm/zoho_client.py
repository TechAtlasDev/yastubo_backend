from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from loguru import logger

from app.core.config import settings


class ZohoClient:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, base_url: str, enabled: bool):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        if not self.enabled:
            return "disabled"

        now = datetime.now(timezone.utc)
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return self._access_token

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://accounts.zoho.com/oauth/v2/token",
                params={
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            payload = response.json()

        token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 3600))
        self._access_token = token
        self._token_expires_at = now + timedelta(seconds=max(expires_in - 60, 60))
        return token

    async def create_or_update_contact(self, data: dict) -> str | None:
        if not self.enabled:
            logger.info("[CRM-DISABLED] contact sync skipped")
            return "disabled"
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/Contacts/upsert",
                    headers={"Authorization": f"Zoho-oauthtoken {token}"},
                    json={"data": [data], "duplicate_check_fields": ["Email"]},
                )
                response.raise_for_status()
                payload = response.json()

            item = payload.get("data", [{}])[0]
            return item.get("details", {}).get("id")
        except Exception as exc:
            logger.error("[CRM] create_or_update_contact error={}", exc)
            return None

    async def create_or_update_deal(self, data: dict, contact_id: str) -> str | None:
        if not self.enabled:
            logger.info("[CRM-DISABLED] deal sync skipped")
            return "disabled"
        try:
            token = await self._get_access_token()
            payload = {**data, "Contact_Name": contact_id}
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/Deals/upsert",
                    headers={"Authorization": f"Zoho-oauthtoken {token}"},
                    json={"data": [payload], "duplicate_check_fields": ["Deal_Name"]},
                )
                response.raise_for_status()
                body = response.json()

            item = body.get("data", [{}])[0]
            return item.get("details", {}).get("id")
        except Exception as exc:
            logger.error("[CRM] create_or_update_deal error={}", exc)
            return None

    async def update_deal_stage(self, deal_id: str, stage: str) -> bool:
        if not self.enabled:
            logger.info("[CRM-DISABLED] update_deal_stage skipped")
            return True
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.patch(
                    f"{self.base_url}/Deals/{deal_id}",
                    headers={"Authorization": f"Zoho-oauthtoken {token}"},
                    json={"data": [{"id": deal_id, "Stage": stage}]},
                )
            return response.status_code in {200, 202}
        except Exception as exc:
            logger.error("[CRM] update_deal_stage error={}", exc)
            return False


_zoho_client_instance: Optional[ZohoClient] = None


def get_zoho_client() -> ZohoClient:
    global _zoho_client_instance
    if _zoho_client_instance is None:
        _zoho_client_instance = ZohoClient(
            client_id=settings.ZOHO_CLIENT_ID,
            client_secret=settings.ZOHO_CLIENT_SECRET,
            refresh_token=settings.ZOHO_REFRESH_TOKEN,
            base_url=settings.ZOHO_BASE_URL,
            enabled=settings.CRM_ENABLED,
        )
    return _zoho_client_instance
