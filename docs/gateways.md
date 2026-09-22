# Gateways

Il modulo espone classi gateway che implementano pattern Adapter sopra le SDK ufficiali.

## StripeGateway
L'implementazione per Stripe.
- Fornisce un metodo `verify_webhook_signature` che decripta l'HMAC dell'header `Stripe-Signature` per garantire che la chiamata provenga davvero da Stripe.
- Traduce internamente gli Intent in concetti di business `ferrox-py`.

## PayPalGateway (Mock)
Predisposto per l'integrazione con l'API REST di PayPal v2. Segue lo stesso contratto astratto di `StripeGateway`.

### L'interfaccia BaseGateway
Ogni nuovo provider (es. Adyen, Satispay) deve semplicemente estendere `BaseGateway` e implementare i metodi astratti. Il `Container` di Ferrox provvederà a iniettarlo nel Controller di Checkout a seconda delle scelte dell'utente, senza modificare la logica di dominio.
