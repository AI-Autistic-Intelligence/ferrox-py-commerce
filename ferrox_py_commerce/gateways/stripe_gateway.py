import stripe
from ferrox_py.core.provider import injectable
from ferrox_py.integrations.payments import PaymentGateway, CheckoutRequest
from ferrox_py.core.errors import FerroxError

@injectable()
class StripeGateway(PaymentGateway):
    def __init__(self, api_key: str = "", webhook_secret: str = ""):
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret

    async def create_checkout_session(self, request: CheckoutRequest) -> str:
        line_items = [{
            "price_data": {
                "currency": request.currency.lower(),
                "product_data": {"name": item.name},
                "unit_amount": item.amount_cents,
            },
            "quantity": item.quantity,
        } for item in request.items]

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.success_url,
                cancel_url=request.cancel_url,
            )
            return session.url
        except Exception as e:
            raise FerroxError(f"Stripe Checkout Error: {str(e)}", 500)

    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> stripe.Event:
        """
        Cryptographically verifies the HMAC signature of the webhook payload.
        """
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            return event
        except ValueError:
            raise FerroxError("Invalid payload", 400)
        except stripe.error.SignatureVerificationError:
            raise FerroxError("Invalid signature", 400)
