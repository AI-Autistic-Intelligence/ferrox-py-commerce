from fastapi import Request
from pydantic import BaseModel
from typing import List
from ferrox_py.core.controllers import BaseController
from ferrox_py.core.container import Container
from ferrox_py.integrations.payments import CheckoutRequest, LineItem
from ferrox_py.databases.redis import RedisCacheService
from ..gateways.stripe_gateway import StripeGateway
from ..services.transaction_state import TransactionStateService

class CartItemPayload(BaseModel):
    name: str
    amount_cents: int
    quantity: int

class CheckoutPayload(BaseModel):
    provider: str
    items: List[CartItemPayload]
    currency: str = "eur"
    success_url: str = "http://localhost:3000/success"
    cancel_url: str = "http://localhost:3000/cancel"

class CommerceApiController(BaseController):
    """
    Frontend-facing API for starting payments and managing subscriptions.
    """
    def __init__(self, container: Container):
        super().__init__(prefix="/commerce", tags=["Commerce API"])
        
        self.stripe_gateway = StripeGateway()
        redis = container.resolve("RedisCacheService", RedisCacheService())
        self.state_service = TransactionStateService(redis)

        @self.router.post("/checkout")
        async def create_checkout(payload: CheckoutPayload):
            """Creates a checkout session and returns the redirect URL to the frontend."""
            
            # Map frontend payload to internal CheckoutRequest
            req = CheckoutRequest(
                amount_cents=sum(i.amount_cents * i.quantity for i in payload.items),
                currency=payload.currency,
                items=[LineItem(name=i.name, amount_cents=i.amount_cents, quantity=i.quantity) for i in payload.items],
                success_url=payload.success_url,
                cancel_url=payload.cancel_url,
            )
            
            if payload.provider.lower() == "stripe":
                checkout_url = await self.stripe_gateway.create_checkout_session(req)
                
                # In a real scenario, you'd extract the Session ID from the Stripe response 
                # and initialize its state to PENDING in the State Machine before returning.
                # await self.state_service.transition_state(session_id, "PENDING")
                
                return self.ok({"checkout_url": checkout_url}, "Stripe Session Created")
            else:
                return self.bad_request("Unsupported provider")

        @self.router.get("/invoices")
        async def list_invoices(request: Request):
            """Returns invoice history (Mock implementation)."""
            return self.ok({"invoices": []}, "Invoices retrieved")
