# Ferrox-Py-Commerce Overview

Il modulo `ferrox-py-commerce` è progettato per gestire in modo sicuro le logiche di billing, processamento pagamenti e riconciliazione contabile.

## Il Problema dei Pagamenti Moderni
Le integrazioni di e-commerce soffrono spesso di problemi complessi:
1. **Webhooks fuori sequenza**: Un evento `invoice.paid` potrebbe arrivare *prima* di `charge.succeeded` a causa di delay di rete di Stripe.
2. **Doppie Ricariche**: Un utente preme due volte "paga" e partono due intent di pagamento concorrenti.
3. **Lock-In al Provider**: Se domani passi da Stripe a PayPal, devi riscrivere tutta la logica dei webhooks e dei checkout.

## Soluzione Ferrox
Questo modulo risolve i tre problemi usando un'architettura rigorosa:
- **Macchina a Stati su Redis (Transaction State)**: Garantisce l'idempotenza matematica. Un ID transazione può passare solo da `PENDING` a `COMPLETED`.
- **Interfacce Astratte (Gateways)**: Un contratto unificato (`BaseGateway`) permette di chiamare `create_payment` senza curarsi se dietro ci sia Stripe o PayPal.
- **Controller Webhook Standardizzati**: Un traduttore universale converte gli eventi proprietari (Stripe JSON) in eventi Pydantic standardizzati (`PaymentSuccessEvent`).
