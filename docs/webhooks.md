# Webhooks Controller

Il modulo webhooks è l'interfaccia asincrona tra il provider di pagamento (es. Stripe) e l'applicazione Ferrox.

## Il Problema del Vendor Lock-in
I provider inviano payload JSON molto differenti. Stripe invia un oggetto annidato sotto `data.object`, PayPal ha una struttura completamente diversa.
Scrivere logica di business legata alla sintassi di Stripe lega a doppio filo il database con il provider.

## WebhooksController come Traduttore
`ferrox-py-commerce` risolve questo disaccoppiando l'ingestion:
1. **Verifica HMAC**: Viene validata la provenienza (es. `Stripe-Signature`).
2. **Parsing**: Il payload del vendor viene ispezionato.
3. **Mappatura**: L'evento viene "tradotto" in un modello di dominio puro (`PaymentSuccessEvent`, `InvoicePaidEvent`, ecc.) definito in `models/events.py`.
4. **Dispatch**: Viene inoltrato alla logica core (Livello 7 della Onion Pipeline), che a questo punto non sa e non gli interessa se l'evento derivi da Stripe o PayPal.
