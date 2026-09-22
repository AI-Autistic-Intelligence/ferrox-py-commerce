# Transaction State (Idempotency and Redis)

## 1. Overview (What does this do?)
The Transaction State module provides a highly concurrent, distributed State Machine designed specifically for managing the lifecycle of financial transactions. It ensures that incoming payment updates (like webhooks) are processed exactly once and in a logically sound order.

## 2. Philosophy (Why does it exist?)
When handling real money, idempotency is not just a nice-to-have architectural feature; it is a strict legal and operational requirement. The system must never credit a user twice for the same payment, even if Stripe sends the `charge.succeeded` webhook three times due to network retries. This module exists to shift the burden of idempotency off the SQL database and onto a blazing-fast in-memory layer (Redis), preventing database locks and race conditions entirely.

## 3. Target Audience (Who is it for?)
This module is for backend developers and DevOps engineers tasked with scaling e-commerce platforms across multiple server nodes (e.g., Kubernetes pods), where concurrent webhook processing could result in severe data corruption without distributed locking.

## 4. Architecture (How does it work?)
- **Atomic Check-and-Set**: When a `PaymentSuccessEvent` webhook arrives, the service queries Redis. If the transaction ID is already marked as `COMPLETED`, the request is immediately discarded. This neutralizes duplicate webhooks instantly.
- **Out of Order Resolution**: If Stripe delivers an `invoice.paid` event before a `charge.succeeded` event due to internal network latency, the State Machine queues or recognizes the missing transition. It strictly rejects invalid state jumps (e.g., transitioning from `FAILED` directly to `COMPLETED`).
- **Redis as a Single Source of Truth**: Because Redis operations are single-threaded and memory-based, collisions between two Kubernetes pods processing the exact same webhook simultaneously are resolved natively at the cache level before touching the SQL database.

## 5. Installation / Setup
This module requires the `ferrox-py-commerce` package, a running Redis server, and the python `redis` client.

```bash
pip install redis
```

## 6. Quickstart (Usage)
```python
from ferrox_py_commerce.services.transaction_state import TransactionStateService

# Usually injected by the IoC container
state_service = TransactionStateService(redis_client)

async def handle_payment_success(transaction_id: str):
    # This method attempts to transition the state atomically in Redis.
    # If another pod already did it, it raises an IdempotencyError or returns False.
    success = await state_service.transition_to(transaction_id, new_state="COMPLETED")
    
    if success:
        print("Payment applied to user account.")
    else:
        print("Payment already processed. Ignoring duplicate webhook.")
```

## 7. Ecosystem Integration
The Transaction State Machine relies fundamentally on the **Security Component** of the core `ferrox-py` framework, utilizing its `RedisLock` (Redlock algorithm) implementation. It also heavily interacts with the **Data Component** to eventually sync the finalized, deduplicated transaction state back to the persistent SQL database.
