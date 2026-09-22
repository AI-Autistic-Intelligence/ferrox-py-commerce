# Controllers

Questo modulo implementa la fascia 6 (Controller Layer) della Onion Pipeline.

## CommerceApiController
Espone gli endpoint per il front-end:
- Creazione di un Checkout Session (restituisce la URL a cui redirigere l'utente).
- Ritorno (Success URL / Cancel URL).
Questo controller invoca il `Gateway` ma *non* salva l'effettivo compimento dell'ordine.

## WebhooksController
(Vedi docs `webhooks.md`). È l'endpoint senza autenticazione ma con verifica HMAC esposto per ricevere le chiamate server-to-server dai provider.

Entrambi i controller delegano l'effettivo salvataggio su DB ai Servizi (Fascia 7), assicurandosi che non ci siano leaky abstractions nei controller stessi.
