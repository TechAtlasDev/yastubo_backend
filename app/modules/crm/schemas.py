from pydantic import BaseModel


class ZohoSyncResult(BaseModel):
    success: bool
    external_id: str | None = None
    message: str | None = None
