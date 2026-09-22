# Transaction State (Idempotenza e Redis)

Quando si maneggiano soldi reali, l'idempotenza non è opzionale, è un requisito legale.

## TransactionStateService
Servizio che si appoggia a **Redis** per mantenere una Macchina a Stati (State Machine) effimera o distribuita, in modo da resistere ai problemi di concorrenza.

### Come previene i problemi
- **Check-and-Set Atomico**: Quando arriva un webhook `PaymentSuccessEvent`, il servizio cerca la transazione su Redis. Se è già in stato `COMPLETED`, ignora la richiesta (gestendo così eventuali webhook duplicati).
- **Out of Order**: Se Stripe invia `invoice.paid` prima di `charge.succeeded` per un ritardo di rete interno a loro, la Macchina a Stati accoda o riconosce la transizione mancante, rifiutando transizioni invalide (es. `FAILED` -> `COMPLETED`).

### Redis come Single Source of Truth Veloce
Viene usato Redis perché è memory-based e atomico. Le collisioni (es. due pod Kubernetes che processano lo stesso Webhook contemporaneamente) vengono bloccate nativamente grazie al check atomico, prevenendo di accreditare i soldi due volte all'utente.
