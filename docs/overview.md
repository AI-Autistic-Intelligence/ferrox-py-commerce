# Ferrox-Py-Commerce Overview

## 1. Overview (What does this do?)
The `ferrox-py-commerce` module is specifically engineered to safely and efficiently manage billing logic, payment processing, and accounting reconciliation within the Ferrox-Py ecosystem.

## 2. Philosophy (Why does it exist?)
Modern e-commerce integrations suffer from three highly complex issues:
1. **Out-of-Sequence Webhooks**: Due to network delays, a provider like Stripe might send an `invoice.paid` event *before* the `charge.succeeded` event.
2. **Double Charges**: A user clicks the "Pay" button twice in rapid succession, launching two concurrent payment intents.
3. **Vendor Lock-In**: Tying domain logic to Stripe's specific JSON syntax makes switching to PayPal financially prohibitive.
This module exists to solve all three problems through a rigorous, highly decoupled architecture.

## 3. Target Audience (Who is it for?)
This overview is for backend engineers and technical leads who need a resilient, fault-tolerant infrastructure to handle real money transactions. If you need a billing system that won't randomly credit users twice due to a network glitch, this framework provides the blueprint.

## 4. Architecture (How does it work?)
The solution relies on three foundational pillars:
- **Redis Transaction State Machine**: Guarantees mathematical idempotency. A transaction ID is locked atomically and can only transition linearly (e.g., from `PENDING` to `COMPLETED`), completely neutralizing duplicate webhooks or concurrent clicks.
- **Abstract Gateways**: A unified interface (`BaseGateway`) allows the system to trigger `create_payment` without caring if the underlying implementation is Stripe, PayPal, or a mock testing environment.
- **Standardized Webhook Controllers**: A universal translator that converts proprietary provider payloads (Stripe JSON) into standardized internal Pydantic events (like `PaymentSuccessEvent`).

## 5. Installation / Setup
```bash
pip install ferrox-py-commerce redis
```
A running Redis instance is strictly required to enable the distributed locking and transaction state management mechanisms.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.container import Container
from ferrox_py_commerce import CommerceModule

# Initializing the billing system requires registering the module.
container = Container()
container.register_module(CommerceModule)
# All controllers, gateways, and state machines are now active.
```

## 7. Ecosystem Integration
The commerce logic integrates perfectly with the core **CQRS Bus**. When the Standardized Webhook Controller parses a successful payment, it dispatches an Event to the bus. Other microservices (like a Notification service sending a receipt email, or a provisioning service unlocking premium features) simply subscribe to the Bus, remaining completely uncoupled from the billing module itself.
