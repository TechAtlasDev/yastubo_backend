import os
import uuid
from typing import Optional
from wallet.passbook import Pass, StoreCard
from app.modules.emission.models import Policy, Client
from app.core.config import settings

class PassbookService:
    def __init__(self):
        # Paths to certificates (to be configured in .env)
        self.cert_path = os.getenv("APPLE_PASS_CERT_PATH")
        self.key_path = os.getenv("APPLE_PASS_KEY_PATH")
        self.wwdr_path = os.getenv("APPLE_WWDR_CERT_PATH")

    async def generate_policy_pass(self, policy: Policy, client: Client) -> bytes:
        """
        Generates a .pkpass file for the policy.
        """
        # Create a StoreCard pass (or Generic)
        card = StoreCard()
        
        # Add basic info
        card.add_primary_field("policy", policy.policy_number, "Póliza")
        card.add_secondary_field("client", f"{client.first_name} {client.last_name}", "Titular")
        
        # Add dates
        if policy.start_date:
            card.add_auxiliary_field("start", str(policy.start_date), "Desde")
        if policy.end_date:
            card.add_auxiliary_field("end", str(policy.end_date), "Hasta")
            
        card.add_back_field("status", policy.status, "Estado")
        card.add_back_field("plan", policy.plan_version_snapshot.get("name", "Plan Yastubo"), "Plan")
        
        # Visuals
        card.barcode = {
            "format": "PKBarcodeFormatQR",
            "message": f"https://yastubo.com/verify/{policy.policy_number}",
            "messageEncoding": "iso-8859-1"
        }
        card.background_color = "rgb(0, 102, 204)"
        card.foreground_color = "rgb(255, 255, 255)"
        
        # Create the Pass object
        pass_obj = Pass(
            card,
            pass_type_identifier=os.getenv("APPLE_PASS_TYPE_ID", "pass.com.yastubo.policy"),
            organization_name="Yastubo",
            team_identifier=os.getenv("APPLE_TEAM_ID", "YASTUBO_TEAM"),
            serial_number=str(policy.id)
        )
        
        # Return the signed .pkpass as bytes
        # In a real scenario, we need the certificates to sign it.
        # For now, we return a placeholder or handle the signing if certs exist.
        if self.cert_path and os.path.exists(self.cert_path):
            # signing logic would go here
            return b"SIGNED_PASS_CONTENT_PLACEHOLDER"
        
        return b"UNSIGNED_PASS_CONTENT_PLACEHOLDER"

_passbook_service: Optional[PassbookService] = None

def get_passbook_service() -> PassbookService:
    global _passbook_service
    if _passbook_service is None:
        _passbook_service = PassbookService()
    return _passbook_service
