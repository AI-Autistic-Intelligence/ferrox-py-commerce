# Controllers

## 1. Overview (What does this do?)
This module implements Layer 6 (Controller Layer) of the Onion Pipeline specifically for the Commerce domain. It exposes the HTTP endpoints required to interact with front-end clients (initiating checkouts) and third-party servers (receiving webhooks).

## 2. Philosophy (Why does it exist?)
The philosophy of the Controller Layer in `ferrox-py` is to remain as "thin" as possible. Controllers should not contain any domain logic or direct database interactions. This module exists strictly to handle HTTP routing, parse incoming network requests, and delegate the actual heavy lifting to the internal Services (Layer 7), thereby preventing "leaky abstractions".

## 3. Target Audience (Who is it for?)
This module is for developers integrating the frontend application (React, Vue, etc.) with the backend billing system, providing them with predictable REST endpoints to generate checkout sessions and redirect users.

## 4. Architecture (How does it work?)
- **CommerceApiController**: Exposes standard endpoints for the front-end. For example, creating a Checkout Session returns the redirect URL (Success URL / Cancel URL). It invokes the `Gateway` abstraction to generate this URL but *never* saves the actual completion of the order.
- **WebhooksController**: An unauthenticated (but cryptographically verified) endpoint exposed to the public internet to receive server-to-server calls from providers like Stripe or PayPal.

## 5. Installation / Setup
These controllers are part of the `ferrox-py-commerce` package. No additional setup is required beyond ensuring your `FerroxApp` is configured to route traffic to the registered module controllers.

## 6. Quickstart (Usage)
```python
# The Controller is automatically registered, but here is a conceptual overview of its usage:
# POST /api/commerce/checkout
# Body: { "price_id": "price_12345", "quantity": 1 }

# The controller delegates to the internal gateway:
class CommerceApiController:
    async def create_checkout(self, payload: CheckoutPayload, gateway: BaseGateway):
        # 1. Ask gateway for URL
        session_url = await gateway.create_checkout_session(payload)
        # 2. Return URL to frontend
        return {"redirect_url": session_url}
```

## 7. Ecosystem Integration
These controllers act as the bridge between the external network and the internal **Gateways** and **Transaction State Machines**. The `WebhooksController` specifically relies heavily on the **Event Dispatcher (CQRS)** from the core ecosystem to broadcast standardized payment events into the system once a payload is verified.
