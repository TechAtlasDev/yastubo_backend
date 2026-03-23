import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.modules.payments.models import Transaction, Subscription

class CreatePaymentIntentRequest(BaseModel):
    policy_id: uuid.UUID
    payment_method_id: Optional[str] = None
    save_payment_method: bool = False

class CreateSubscriptionRequest(BaseModel):
    policy_id: uuid.UUID
    stripe_payment_method_id: str
    billing_anchor_day: Optional[int] = Field(None, ge=1, le=28)

class ManualPaymentRequest(BaseModel):
    policy_id: uuid.UUID
    amount: Decimal
    notes: Optional[str] = None

class CancelSubscriptionRequest(BaseModel):
    policy_id: uuid.UUID
    cancel_immediately: bool = False

class TransactionResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    stripe_payment_intent_id: Optional[str]
    stripe_invoice_id: Optional[str]
    amount: Decimal
    currency: str
    status: str
    payment_type: str
    processed_at: Optional[datetime]
    client_secret: Optional[str] = None # For PI response
    model_config = ConfigDict(from_attributes=True)

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    model_config = ConfigDict(from_attributes=True)

class ConnectOnboardingResponse(BaseModel):
    url: str
    account_id: str
