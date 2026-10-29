# PySyriatel

Python clients for Syriatel Cash API v2 and existing v1 integrations.

```bash
pip install --upgrade PySyriatel
```

## Read incoming payments

```python
import os
from syriatel import SyriatelV2Sync

with SyriatelV2Sync(os.environ["SYRIATEL_API_TOKEN"]) as client:
    result = client.incoming_transactions(
        gsm="0912345678", start_at="2026-10-29", limit=20
    )
    for transfer in result["transactions"]:
        print(transfer["transaction_no"], transfer["amount"])
    balance = client.get_balance(pay_code="00123456")
```

Supply exactly one of `gsm` or `pay_code`. Both are strings; preserve leading
zeros. Incoming results support inclusive `start_at` / `end_at`, repeated
`transaction_ids`, `limit` (1–200), and `page` (from 1). Date-only bounds use
Asia/Damascus. Paid numbers use stored incoming history; trials read live provider
pages and filter the selected page. `updated_at` identifies the synchronization
cutoff. Treat `HISTORY_SYNCING` as a retryable unavailable result, never as an
empty transfer list. Honour `Retry-After`. The client never retries purchases.

The async client has the same methods:

```python
import asyncio, os
from syriatel import SyriatelV2

async def main():
    async with SyriatelV2(os.environ["SYRIATEL_API_TOKEN"]) as client:
        result = await client.incoming_transactions(gsm="0912345678")
        print(result["transactions"])

asyncio.run(main())
```

## Akrab Elik accounts and their numbers

An account is one linked Akrab Elik login. Child GSMs are numbers.

```python
with SyriatelV2Sync(os.environ["SYRIATEL_API_TOKEN"]) as client:
    accounts = client.list_accounts()
    for account in accounts:
        for number in client.list_numbers(account["id"]):
            print(number["gsm"], number["pay_code"], number["subscription"])
```

`list_accounts()` and `list_numbers(account_id)` return lists directly. Other
methods return the HTTP envelope's `data` object. Money values are decimal strings.
Keep the token on your server. Enable **Manage accounts and subscriptions** under
Dashboard → API before calling methods that change accounts, PIN verification,
subscriptions or renewal preferences. Read requests do not need this permission.

| Method | Purpose |
|---|---|
| `incoming_transactions(gsm=... / pay_code=..., ...)` | Incoming transfers |
| `get_balance(gsm=... / pay_code=...)` | Number cash balance |
| `list_accounts()` | Linked Akrab Elik accounts |
| `list_numbers(account_id)` | All child numbers and subscription details |
| `get_plans()` | Authenticated, discounted prices |
| `wallet_balance()` | Platform USD balance only |
| `create_link_session(gsm, password, idempotency_key=...)` | Start account linking |
| `get_link_session(session_id)` | Check linking state |
| `verify_link_session(session_id, code)` | Complete SMS verification |
| `verify_pin(account_id, gsm, pin)` | Verify a four-digit PIN |
| `subscribe(account_id, gsm, idempotency_key=..., plan_id="monthly", periods=1)` | Purchase or extend access |
| `start_trial(account_id, gsm, idempotency_key=...)` | Activate an eligible trial |
| `set_auto_renew(account_id, gsm, enabled)` | Change renewal separately |
| `remove_account(account_id)` | Unlink an Akrab Elik account and its child numbers |
| `get_status()` | Public availability announcement |

PIN and SMS codes must be strings of exactly four and six digits respectively.
Subscription requests preserve the existing auto-renew preference. Use a unique
Idempotency-Key for each intentional purchase; reuse that key only when retrying
the same operation and body. Individual child numbers cannot be removed in v2.

## Existing v1 clients

`SyriatelAPI`, `SyriatelAPISync` and their `syrcash` methods retain the v1 contract,
including outgoing-history compatibility. Use `SyriatelV2` / `SyriatelV2Sync` for
the parent-account hierarchy. Never use a synchronous client inside an async loop.

## Releases

Changing the version on master or pushing its matching `vX.Y.Z` tag runs client
checks, builds and validates the distributions, publishes to PyPI, then creates a
release. Tags must match the package version. Configure `PYPI_API_TOKEN` in the
repository's Actions secrets, or configure its trusted PyPI publisher. Publication
failures fail the release workflow.

[API reference](https://api.melchersman.com/syr-cash/en/docs)
