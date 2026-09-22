from ferrox_py.core.provider import injectable
from ferrox_py.integrations.payments import PaymentGateway, CheckoutRequest

@injectable()
class PayPalGateway(PaymentGateway):
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        
    async def create_checkout_session(self, request: CheckoutRequest) -> str:
        # Mocking PayPal REST API call for creating an order
        print(f"PayPal: Creating order for {sum(i.amount_cents for i in request.items)} cents")
        return "https://www.sandbox.paypal.com/checkoutnow?token=mock_token_123"

    def verify_webhook_signature(self, headers: dict, body: dict) -> bool:
        """
        PayPal requires a complex certificate/signature verification.
        In production, this calls PayPal's /v1/notifications/verify-webhook-signature API.
        """
        # Mock verification
        if "paypal-transmission-sig" in headers:
            return True
        return False
