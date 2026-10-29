# PySyriatel

A Python client for the Syriatel Cash platform. Both synchronous and asynchronous
clients use the API Token from your account's API page.

## Install

```bash
pip install "PySyriatel @ https://github.com/Melchersman/PySyriatel/releases/download/v2.2.0/pysyriatel-2.2.0-py3-none-any.whl"
```

[API reference and response examples](https://api.melchersman.com/syr-cash/en/docs)

## Read your numbers

```python
import asyncio
import os
from syriatel import SyriatelAPI

async def main():
    async with SyriatelAPI(os.environ["SYRIATEL_API_TOKEN"]) as client:
        numbers = await client.list_accounts()
        for number in numbers:
            print(number["phone"], number["subscription"]["status"])

asyncio.run(main())
```

For synchronous code:

```python
import os
from syriatel import SyriatelAPISync

with SyriatelAPISync(os.environ["SYRIATEL_API_TOKEN"]) as client:
    numbers = client.list_accounts()
    profile = client.get_profile()
```

Use `SyriatelAPI` inside an async application. Use a context manager or call
`close()` when you finish. A supplied `aiohttp.ClientSession` stays caller-owned.

## Link an Akrab Elik account

Enable **Manage accounts and subscriptions** on the API page before making
management calls. The same token continues to work for reads.

```python
import os
from uuid import uuid4
from syriatel import SyriatelAPISync

with SyriatelAPISync(os.environ["SYRIATEL_API_TOKEN"]) as client:
    request_key = str(uuid4())
    session = client.create_link_session(
        "0991234567", os.environ["AKRAB_PASSWORD"],
        idempotency_key=request_key,
    )
    if session["status"] == "verification_required":
        session = client.verify_link_session(session["id"], input("SMS code: "))
    if session["status"] == "linked":
        for number in session["accounts"]:
            print(number["id"], number["phone"])
```

Pass SMS codes and PINs as strings so leading zeros are preserved. A PIN has four
digits; an Akrab Elik SMS code has six. Reading a link session does not send SMS.

## Verify and subscribe

```python
import os
from uuid import uuid4
from syriatel import SyriatelAPISync

with SyriatelAPISync(os.environ["SYRIATEL_API_TOKEN"]) as client:
    number = client.verify_pin("acc_YOUR_ACCOUNT_ID", input("PIN: "))
    purchase_key = str(uuid4())
    result = client.subscribe(
        number["id"], periods=1, auto_renew=True,
        idempotency_key=purchase_key,
    )
    print(result["expires_at"], result["charged_usd"])
```

Keep the same purchase key and body after a network failure. Generate a new key
for a new purchase. The client never retries a purchase automatically. USD values
are decimal strings; use `decimal.Decimal` when doing calculations.

## Methods

Both clients expose these methods. Await them on `SyriatelAPI`.

| Method | Result |
| --- | --- |
| `get_profile()` | Platform profile and wallet preferences |
| `get_plans()` | Pricing with your discount |
| `list_accounts()` | All linked numbers, including unverified or expired ones |
| `get_account(account_id)` | One number |
| `rename_account(account_id, name)` | Updated number |
| `remove_account(account_id)` | Removal result |
| `create_link_session(phone, password, idempotency_key=...)` | Link session |
| `get_link_session(session_id)` | Current link state and linked numbers |
| `verify_link_session(session_id, code)` | Updated link session |
| `cancel_link_session(session_id)` | Cancellation result |
| `verify_pin(account_id, pin)` | Verified number and pay code |
| `start_trial(account_id, idempotency_key=..., auto_renew=...)` | Trial result |
| `subscribe(account_id, idempotency_key=..., periods=1, auto_renew=...)` | Purchase or extension result |
| `get_subscription(account_id)` | Subscription state |
| `update_subscription(account_id, auto_renew=..., paused=...)` | Updated subscription |
| `disable_auto_renew(account_id)` | Updated renewal preference |
| `get_balance(account_id)` | Cash balance in SYP |
| `get_transactions(account_id, direction="incoming", page=1, search="")` | Incoming or outgoing history |
| `get_wallet(limit=50, before_id=...)` | USD wallet and paginated ledger |
| `get_public_plans()` | Public pricing |
| `get_service_status()` | Maintenance status |

Methods return the response's `data` value. `list_accounts()` unwraps its
`accounts` list. The API reference shows the complete HTTP response envelopes.

## Rate limits and errors

Balance and both history directions share a request budget for each number.
Use one polling worker and respect `Retry-After`.

```python
from syriatel import RateLimitError, SubscriptionExpiredError

try:
    result = await client.get_balance("acc_YOUR_ACCOUNT_ID")
except RateLimitError as error:
    print("Wait", error.retry_after, "seconds")
except SubscriptionExpiredError:
    print("Activate or renew the number's subscription")
```

Errors expose `code`, `status_code`, `request_id` and `retry_after` where available.
`InvalidTokenError`, `ManagementDisabledError`, `InsufficientBalanceError` and
`IdempotencyConflictError` distinguish account actions from network failures.

## Existing integrations

Existing `get_numbers()`, `get_codes()`, `get_numbers_codes()` and `syrcash`
methods remain available. Inventory contains only eligible active numbers.
Use `list_accounts()` when managing numbers that are unverified or expired.

```python
numbers = await client.get_numbers()
codes = await client.get_codes()
pairs = await client.get_numbers_codes()
balance = await client.syrcash.balance("0991234567")
incoming = await client.syrcash.get_incoming_history(number="0991234567")
outgoing = await client.syrcash.get_outgoing_history(number="0991234567")
transaction = await client.syrcash.find_incoming_transaction(
    "TXN123456", number="0991234567"
)
```

Legacy history calls return `Transaction` objects. The newer
`get_transactions()` returns the full history data, including pagination and
cache information.

## License

MIT. See [LICENSE](LICENSE).
