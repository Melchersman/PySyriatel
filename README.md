# PySyriatel

Python client for Syriatel API.

## Installation

```bash
pip install PySyriatel
```

## Usage

### Async

```python
from syriatel import SyriatelAPI

async with SyriatelAPI(api_token="your_token") as api:
    # Get registered numbers
    numbers = await api.get_numbers()
    codes = await api.get_codes()
    numbers_codes = await api.get_numbers_codes()
    
    # Syriatel Cash
    balance = await api.syrcash.balance("0991234567")  # By number
    balance = await api.syrcash.balance(code="65288500")  # By secret code
    
    incoming = await api.syrcash.get_incoming_history(
        number="0991234567",
        start_at="2024-01-01",
        end_at="2024-12-31"
    )
    
    outgoing = await api.syrcash.get_outgoing_history(number="0991234567")
    
    tx = await api.syrcash.find_incoming_transaction(
        "TXN123456",
        number="0991234567"
    )
```

### Sync

```python
from syriatel import SyriatelAPISync

with SyriatelAPISync(api_token="your_token") as api:
    numbers = api.get_numbers()
    balance = api.syrcash.balance("0991234567")
    incoming = api.syrcash.get_incoming_history(number="0991234567")
```

## API

### SyriatelAPI / SyriatelAPISync

| Method | Returns | Description |
|--------|---------|-------------|
| `get_numbers()` | `List[str]` | Active phone numbers |
| `get_codes()` | `List[str]` | Secret codes |
| `get_numbers_codes()` | `List[Tuple[str, str]]` | Number and code pairs |

### api.syrcash

| Method | Returns | Description |
|--------|---------|-------------|
| `balance(number=None, code=None)` | `int` | Balance in SYP. Accepts either `number` or `code` parameter |
| `get_incoming_history(number, code, page, start_at, end_at)` | `List[Transaction]` | Incoming transfers |
| `get_outgoing_history(number, code, page, start_at, end_at)` | `List[Transaction]` | Outgoing transfers |
| `find_incoming_transaction(transaction_no, number, code)` | `Transaction` | Find by transaction number |

### Transaction

```python
@dataclass
class Transaction:
    transaction_no: str
    date: str
    from_gsm: str
    to_gsm: str
    amount: int
    fee: int
    net: int
    channel: str
    status: str
```

## Error Handling

```python
from syriatel import (
    SyriatelAPIError,
    InvalidTokenError,
    SubscriptionExpiredError,
    FetchFailedError,
    NetworkError,
)

try:
    balance = await api.syrcash.balance("0991234567")
except SubscriptionExpiredError:
    print("Subscription expired")
except InvalidTokenError:
    print("Invalid token")
except NetworkError as e:
    print(f"Network error: {e}")
```

## License

MIT
