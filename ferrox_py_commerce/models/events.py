from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class PaymentSuccessEvent(BaseModel):
    """
    Standardized event emitted when ANY provider successfully processes a payment.
    """
    provider: str  # 'stripe', 'paypal'
    transaction_id: str
    amount_cents: int
    currency: str
    customer_email: Optional[str]
    metadata: Dict[str, str] = {}
    timestamp: datetime = datetime.utcnow()

class SubscriptionCreatedEvent(BaseModel):
    """
    Standardized event for new SaaS subscriptions.
    """
    provider: str
    subscription_id: str
    customer_id: str
    plan_id: str
    status: str

class InvoicePaidEvent(BaseModel):
    """Event for successful recurring SaaS payments."""
    provider: str
    invoice_id: str
    subscription_id: str
    customer_id: str
    amount_cents: int
    currency: str
    timestamp: datetime = datetime.utcnow()

class InvoiceFailedEvent(BaseModel):
    """Event for failed recurring SaaS payments (card declined)."""
    provider: str
    invoice_id: str
    subscription_id: str
    customer_id: str
    timestamp: datetime = datetime.utcnow()
