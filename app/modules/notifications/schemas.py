from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailAttachment(BaseModel):
    filename: str
    content: str
    type: str


class EmailMessage(BaseModel):
    to_email: EmailStr
    to_name: str
    subject: str
    html_content: str
    attachments: Optional[list[EmailAttachment]] = None


class WhatsAppMessage(BaseModel):
    to_phone: str
    message: str
