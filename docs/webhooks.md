# Webhooks Controller

## 1. Overview (What does this do?)
The Webhooks Controller is the asynchronous interface between external payment providers (e.g., Stripe, PayPal) and the internal Ferrox application. It acts as a universal translator, securely receiving HTTP POST requests, verifying their authenticity, and converting them into internal domain events.

## 2. Philosophy (Why does it exist?)
Payment providers send JSON payloads that differ vastly in structure. Stripe nests data under `data.object`, while PayPal uses a completely different schema. Writing business logic that depends directly on Stripe's specific JSON syntax tightly couples the core database to a third-party vendor. The philosophy here is absolute decoupling: the business logic must never know which provider sent the payment.

## 3. Target Audience (Who is it for?)
This component is for backend developers who need to expose secure, public-facing endpoints to ingest asynchronous events from third-party APIs without exposing the internal application logic to vendor-specific data structures.

## 4. Architecture (How does it work?)
`ferrox-py-commerce` solves the vendor lock-in problem through a strict 4-step ingestion pipeline:
1. **HMAC Verification**: The controller extracts the cryptographic signature (e.g., `Stripe-Signature`) from the HTTP headers and validates it using the injected **Gateway** adapter.
2. **Parsing**: The raw, vendor-specific JSON payload is inspected.
3. **Mapping**: The proprietary event is "translated" into a pure, standardized Pydantic domain model (e.g., `PaymentSuccessEvent`, `InvoicePaidEvent`) defined in the `models/events.py` file.
4. **Dispatch**: The standardized Pydantic model is forwarded to the core logic (Layer 7 of the Onion Pipeline). At this point, the business logic only sees a generic `PaymentSuccessEvent` and has no awareness of the original provider.

## 5. Installation / Setup
The Webhooks Controller is built-in. It simply requires configuring the provider-specific webhook signing secrets in your environment variables so the HMAC verification step can function correctly.

## 6. Quickstart (Usage)
```python
# The Controller is pre-configured, but internally it operates like this:
from ferrox_py_commerce.gateways.base import BaseGateway
from ferrox_py_commerce.models.events import PaymentSuccessEvent

class WebhooksController:
    async def stripe_webhook(self, request, gateway: BaseGateway, event_bus):
        # 1. Verify Signature
        is_valid = await gateway.verify_webhook_signature(
            payload=request.body, 
            signature=request.headers.get("Stripe-Signature"),
            secret=STRIPE_WEBHOOK_SECRET
        )
        if not is_valid:
            raise ForbiddenError("Invalid HMAC signature")
            
        # 2 & 3. Parse and Map (Abstracted in real implementation)
        event = PaymentSuccessEvent(transaction_id="txn_123", amount=10.00)
        
        # 4. Dispatch generic event
        await event_bus.dispatch(event)
        return {"status": "success"}
```

## 7. Ecosystem Integration
The Webhooks Controller relies heavily on the **CQRS and Event Dispatcher** core module. Instead of invoking database repositories directly, the controller broadcasts the translated `PaymentSuccessEvent` to the Event Bus. The **Transaction State** service, listening on that bus, then picks up the event to enforce idempotency.
