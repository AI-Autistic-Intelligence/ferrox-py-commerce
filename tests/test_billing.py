import pytest
from ferrox_py.integrations.payments import CheckoutRequest, PaymentItem
from ferrox_py_commerce.gateways.paypal_gateway import PayPalGateway

@pytest.mark.asyncio
async def test_paypal_create_checkout():
    gateway = PayPalGateway()
    req = CheckoutRequest(
        amount_cents=1000,
        currency="usd",
        items=[PaymentItem(name="Test", amount_cents=1000, quantity=1)],
        success_url="http://test/success",
        cancel_url="http://test/cancel"
    )
    url = await gateway.create_checkout_session(req)
    assert "paypal.com" in url

def test_paypal_verify_signature():
    gateway = PayPalGateway()
    # It's a mock that returns true if header present
    assert gateway.verify_webhook_signature({"paypal-transmission-sig": "abc"}, {}) is True
    assert gateway.verify_webhook_signature({}, {}) is False
