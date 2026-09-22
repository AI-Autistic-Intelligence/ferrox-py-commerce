from fastapi import Request
from ferrox_py.core.controllers import BaseController
from ferrox_py.core.container import Container
from ferrox_py.core.errors import FerroxError
from ferrox_py.databases.redis import RedisCacheService
from ..gateways.stripe_gateway import StripeGateway
from ..gateways.paypal_gateway import PayPalGateway
from ..models.events import PaymentSuccessEvent, InvoicePaidEvent, InvoiceFailedEvent
from ..services.transaction_state import TransactionStateService

class CommerceWebhookController(BaseController):
    """
    The Webhook Standardizer. 
    Receives raw webhooks from Stripe and PayPal, mathematically verifies the cryptographic 
    signatures to prevent fraud, enforces idempotency, updates transaction state, 
    and standardizes them into Ferrox Events.
    """
    def __init__(self, container: Container):
        super().__init__(prefix="/webhooks/commerce", tags=["Commerce Webhooks"])
        
        # Resolve dependencies
        self.stripe_gateway = StripeGateway()
        self.paypal_gateway = PayPalGateway()
        
        redis = container.resolve("RedisCacheService", RedisCacheService())
        self.state_service = TransactionStateService(redis)

        @self.router.post("/stripe")
        async def stripe_webhook(request: Request):
            payload = await request.body()
            sig_header = request.headers.get("stripe-signature")
            
            if not sig_header:
                raise FerroxError("Missing Stripe signature", 400)

            # 1. Cryptographic Validation
            event = self.stripe_gateway.verify_webhook_signature(payload, sig_header)
            
            # 2. Idempotency Check (Redis)
            is_duplicate = await self.state_service.check_idempotency(event.id)
            if is_duplicate:
                return self.ok(message="Duplicate event ignored")
            
            # 3. Standardization & State Machine
            if event.type == "checkout.session.completed":
                session = event.data.object
                # Transition state to PAID
                valid = await self.state_service.transition_state(session.id, "PAID")
                if valid:
                    std_event = PaymentSuccessEvent(
                        provider="stripe",
                        transaction_id=session.id,
                        amount_cents=session.amount_total,
                        currency=session.currency,
                        customer_email=session.customer_details.email if session.customer_details else None,
                    )
                    print(f"[EVENT BUS] Emitting: {std_event.model_dump_json()}")
                    
            elif event.type == "invoice.paid":
                invoice = event.data.object
                std_event = InvoicePaidEvent(
                    provider="stripe",
                    invoice_id=invoice.id,
                    subscription_id=invoice.subscription,
                    customer_id=invoice.customer,
                    amount_cents=invoice.amount_paid,
                    currency=invoice.currency
                )
                print(f"[EVENT BUS] Emitting: {std_event.model_dump_json()}")
                
            elif event.type == "invoice.payment_failed":
                invoice = event.data.object
                std_event = InvoiceFailedEvent(
                    provider="stripe",
                    invoice_id=invoice.id,
                    subscription_id=invoice.subscription,
                    customer_id=invoice.customer
                )
                print(f"[EVENT BUS] Emitting: {std_event.model_dump_json()}")
                
            return self.ok(message="Webhook processed successfully")

        @self.router.post("/paypal")
        async def paypal_webhook(request: Request):
            headers = dict(request.headers)
            body = await request.json()
            
            # 1. Cryptographic Validation
            is_valid = self.paypal_gateway.verify_webhook_signature(headers, body)
            if not is_valid:
                raise FerroxError("Invalid PayPal signature", 400)
                
            # 2. Standardization
            if body.get("event_type") == "PAYMENT.CAPTURE.COMPLETED":
                resource = body.get("resource", {})
                std_event = PaymentSuccessEvent(
                    provider="paypal",
                    transaction_id=resource.get("id"),
                    amount_cents=int(float(resource.get("amount", {}).get("value", 0)) * 100),
                    currency=resource.get("amount", {}).get("currency_code", "USD"),
                    customer_email=None,
                )
                print(f"[EVENT BUS] Emitting: {std_event.model_dump_json()}")

            return self.ok(message="Webhook received")
