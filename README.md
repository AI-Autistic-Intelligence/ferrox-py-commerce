# Ferrox-Py-Commerce

## 1. Overview (What does this do?)
The `ferrox-py-commerce` package is a standardized extension for the Ferrox ecosystem dedicated to handling billing, subscriptions, and standardized payment webhooks. It abstracts away the complexity of dealing directly with external payment providers (like Stripe or PayPal) and guarantees robust, mathematically idempotent transaction handling.

## 2. Philosophy (Why does it exist?)
Handling real money in software is notoriously difficult. E-commerce integrations frequently suffer from race conditions (double charging a user), out-of-order webhook events (an invoice is marked paid before the charge is completed), and severe vendor lock-in. This module exists to decouple your core business logic from the specific syntax and behavior of third-party payment gateways, enforcing strict state machines that make duplicate charges nearly impossible.

## 3. Target Audience (Who is it for?)
This module is intended for backend engineers building SaaS billing systems, subscription platforms, or general e-commerce architectures where financial data integrity and vendor-agnostic infrastructure are critical.

## 4. Architecture (How does it work?)
The Commerce module leverages three main architectural concepts:
- **Gateways**: Abstract adapters over official provider SDKs (e.g., `StripeGateway`), allowing the core application to initiate payments using uniform interfaces.
- **Transaction State Machine**: A strict, Redis-backed state machine that enforces mathematical idempotency for incoming webhook events (e.g., ensuring a transaction can only move from `PENDING` to `COMPLETED` once).
- **Controllers & Webhooks**: Layer 6 endpoints that securely parse incoming events (verifying HMAC signatures) and translate proprietary JSON payloads into standardized Pydantic Domain Events.

## 5. Installation / Setup
Ensure you are using Python 3.11+ and install the package via pip:

```bash
pip install ferrox-py-commerce
```
You will also need to configure a Redis instance, as it is required by the `TransactionStateService` to manage distributed, atomic locks.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.container import Container
from ferrox_py_commerce import CommerceModule

# 1. Initialize your IoC container
container = Container()

# 2. Register the Commerce Module
container.register_module(CommerceModule)

# The Webhook controllers, Gateways, and State Machines are now 
# wired and ready to process payments safely!
```

## 7. Ecosystem Integration
The Commerce module integrates seamlessly with the **Security Component** of the core `ferrox-py` framework for distributed Redis locking, and it relies strictly on the **AuthModule** (`ferrox-py-auth`) to ensure that payment intents and subscriptions are accurately linked to a validated, authenticated `User` context.
