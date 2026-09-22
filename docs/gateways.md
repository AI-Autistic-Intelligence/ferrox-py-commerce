# Gateways

## 1. Overview (What does this do?)
The Gateways module provides Adapter pattern implementations over official payment provider SDKs (like Stripe or PayPal). It standardizes how the `ferrox-py` application requests checkout sessions, issues refunds, or verifies webhook signatures.

## 2. Philosophy (Why does it exist?)
If your application uses the `stripe` python package directly within your business logic, you suffer from immediate vendor lock-in. If business requirements mandate a switch to PayPal or Adyen, refactoring becomes a massive endeavor. This module exists to define a strict, generic `BaseGateway` interface. The business logic only talks to this interface, completely isolating it from vendor-specific quirks.

## 3. Target Audience (Who is it for?)
This abstraction is crucial for architects designing future-proof SaaS applications, and for backend developers tasked with implementing new payment methods without breaking the existing core billing logic.

## 4. Architecture (How does it work?)
- **BaseGateway**: An abstract Python class defining the core contract (`create_payment`, `refund`, `verify_webhook_signature`).
- **StripeGateway**: The concrete implementation for Stripe. It translates Ferrox intents into Stripe Intents and decrypts the `Stripe-Signature` HMAC headers.
- **PayPalGateway**: A mock/stub implementation ready to be connected to PayPal's REST API v2, following the exact same generic contract.
Through Inversion of Control, the container injects the correct concrete implementation into the controllers based on the environment configuration.

## 5. Installation / Setup
While the `BaseGateway` is built-in, you must install the specific vendor SDKs you plan to use in production.

```bash
pip install stripe
# pip install paypalrestsdk (if using PayPal)
```

## 6. Quickstart (Usage)
```python
from ferrox_py_commerce.gateways.base import BaseGateway
from ferrox_py_commerce.gateways.stripe import StripeGateway

# Developers can implement new gateways easily:
class AdyenGateway(BaseGateway):
    async def verify_webhook_signature(self, payload, signature, secret) -> bool:
        # Custom Adyen HMAC verification logic here
        pass

    async def create_checkout_session(self, items, success_url, cancel_url):
        # Custom Adyen session logic
        pass

# The IoC container registers the desired implementation
# container.register("payment_gateway", StripeGateway(api_key="sk_test_..."))
```

## 7. Ecosystem Integration
Gateways are injected directly into the **Controllers** via the Core IoC Container. They also interface closely with the **WebhooksController**, providing the necessary cryptographic verification methods required to sanitize incoming Layer 1 HTTP requests before they are parsed by the framework.
