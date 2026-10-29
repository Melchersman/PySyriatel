## 2.3.0

- Add SyriatelV2 and SyriatelV2Sync for GSM/pay-code payment reads and Akrab Elik account management.
- Support incoming date and transaction-ID filters, per-number PINs, subscriptions and separate renewal updates.
- Keep the existing v1 clients and their signatures.
- Publish checked releases on version changes and matching version tags.

# Changelog

## 2.2.0

- Add account linking, SMS verification, PIN verification and number management.
- Add plans, trials, purchases, renewals, pause and auto-renew preferences.
- Add account-ID balance/history calls, wallet pagination and service status.
- Preserve API exception types and expose HTTP status, request IDs and Retry-After.
- Keep legacy inventory and `syrcash` methods available.
- Give the synchronous client its own reusable event loop and close it cleanly.
