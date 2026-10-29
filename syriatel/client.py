"""
Syriatel API Client

Supports both async and sync operations.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, List, Tuple
from .exceptions import raise_error, NetworkError, SyriatelAPIError
from .models import Transaction
from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import timezone


class SyriatelCash:
    """
    Syriatel Cash API namespace
    
    Contains methods for interacting with Syriatel Cash services.
    """
    
    def __init__(self, api: "SyriatelAPI"):
        """Initialize the Cash namespace with API client"""
        self._api = api
    
    async def balance(self, number: str) -> int:
        """
        Get Syriatel Cash balance for a phone number
        
        Args:
            number: Phone number in format 0XXXXXXXXX (will be normalized)
            
        Returns:
            Balance as integer (in SYP)
            
        Raises:
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            ServerMaintenanceError: If servers are under maintenance
            NetworkError: If network request fails
        """
        normalized = self._api._normalize_number(number)
        data = await self._api._request("GET", "/Balance", params={"number": normalized})
        return int(data.get("balance", 0))
    
    async def get_incoming_history(
        self,
        number: Optional[str] = None,
        code: Optional[str] = None,
        page: int = 1,
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get incoming transaction history for Syriatel Cash
        
        Args:
            number: Phone number (required if code not provided, will be normalized)
            code: Secret code (required if number not provided)
            page: Page number for pagination (default: 1)
            start_at: Filter transactions from this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            end_at: Filter transactions until this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            List[Transaction] - List of incoming transactions
            
        Raises:
            ValueError: If neither number nor code is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            NetworkError: If network request fails
        """
        if not number and not code:
            raise ValueError("Either 'number' or 'code' must be provided")
        
        params = {"page": page}
        if number:
            params["number"] = self._api._normalize_number(number)
        elif code:
            params["code"] = code
        
        data = await self._api._request("GET", "/IncomingHistory", params=params)
        
        # Return list of transactions directly
        transactions = [
            Transaction.from_dict(tx) for tx in data.get("transactions", [])
        ]
        
        # Apply date filtering if provided
        return self._api._filter_transactions_by_date(transactions, start_at, end_at)
    
    async def get_outgoing_history(
        self,
        number: Optional[str] = None,
        code: Optional[str] = None,
        page: int = 1,
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get outgoing transaction history for Syriatel Cash
        
        Args:
            number: Phone number (required if code not provided, will be normalized)
            code: Secret code (required if number not provided)
            page: Page number for pagination (default: 1)
            start_at: Filter transactions from this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            end_at: Filter transactions until this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            List[Transaction] - List of outgoing transactions
            
        Raises:
            ValueError: If neither number nor code is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            NetworkError: If network request fails
        """
        if not number and not code:
            raise ValueError("Either 'number' or 'code' must be provided")
        
        params = {"page": page}
        if number:
            params["number"] = self._api._normalize_number(number)
        elif code:
            params["code"] = code
        
        data = await self._api._request("GET", "/OutgoingHistory", params=params)
        
        # Return list of transactions directly
        transactions = [
            Transaction.from_dict(tx) for tx in data.get("transactions", [])
        ]
        
        # Apply date filtering if provided
        return self._api._filter_transactions_by_date(transactions, start_at, end_at)
    
    def find_transaction_by_number(
        self,
        transactions: List[Transaction],
        transaction_no: str,
    ) -> Optional[Transaction]:
        """
        Find a transaction by transaction number
        
        Args:
            transactions: List of Transaction objects to search
            transaction_no: Transaction number to search for
            
        Returns:
            Transaction object if found, None otherwise
        """
        for tx in transactions:
            if tx.transaction_no == transaction_no:
                return tx
        return None
    
    async def find_incoming_transaction(
        self,
        transaction_no: str,
        number: Optional[str] = None,
        code: Optional[str] = None,
        max_pages: int = 10,
    ) -> Optional[Transaction]:
        """
        Find an incoming transaction by transaction number
        
        This method searches through multiple pages if needed to find the transaction.
        
        Args:
            transaction_no: Transaction number to search for
            number: Phone number (required if code not provided)
            code: Secret code (required if number not provided)
            max_pages: Maximum number of pages to search (default: 10)
            
        Returns:
            Transaction object if found, None otherwise
        """
        if not number and not code:
            raise ValueError("Either 'number' or 'code' must be provided")
        
        for page in range(1, max_pages + 1):
            transactions = await self.get_incoming_history(number, code, page)
            
            # Search in current page
            tx = self.find_transaction_by_number(transactions, transaction_no)
            if tx:
                return tx
            
            # If we got fewer transactions than expected, we've reached the end
            if len(transactions) == 0:
                break
        
        return None


class SyriatelCashSync:
    """Sync wrapper for SyriatelCash namespace"""
    
    def __init__(self, async_cash: SyriatelCash, run_async_func):
        self._async_cash = async_cash
        self._run_async = run_async_func
    
    def balance(self, number: str) -> int:
        """Get balance (sync)"""
        return self._run_async(self._async_cash.balance(number))
    
    def get_incoming_history(
        self,
        number: Optional[str] = None,
        code: Optional[str] = None,
        page: int = 1,
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Get incoming history (sync)"""
        return self._run_async(
            self._async_cash.get_incoming_history(number, code, page, start_at, end_at)
        )
    
    def get_outgoing_history(
        self,
        number: Optional[str] = None,
        code: Optional[str] = None,
        page: int = 1,
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Get outgoing history (sync)"""
        return self._run_async(
            self._async_cash.get_outgoing_history(number, code, page, start_at, end_at)
        )
    
    def find_transaction_by_number(
        self,
        transactions: List[Transaction],
        transaction_no: str,
    ) -> Optional[Transaction]:
        """Find transaction by number (sync)"""
        return self._async_cash.find_transaction_by_number(transactions, transaction_no)
    
    def find_incoming_transaction(
        self,
        transaction_no: str,
        number: Optional[str] = None,
        code: Optional[str] = None,
        max_pages: int = 10,
    ) -> Optional[Transaction]:
        """Find incoming transaction (sync)"""
        return self._run_async(
            self._async_cash.find_incoming_transaction(
                transaction_no, number, code, max_pages
            )
        )


class SyriatelAPI:
    """
    Async client for Syriatel API
    
    Example:
        ```python
        import asyncio
        from syriatel import SyriatelAPI
        
        async def main():
            async with SyriatelAPI(api_token="your_token") as api:
                # Get numbers
                numbers = await api.get_numbers()
                
                # Use cash namespace
                balance = await api.syrcash.balance("0991234567")
                transactions = await api.syrcash.get_incoming_history("0991234567")
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.melchersman.com/syr-cash/v1",
        timeout: int = 30,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Initialize the async API client
        
        Args:
            api_token: Your API token
            base_url: Base URL for the API (default: production URL)
            timeout: Request timeout in seconds (default: 30)
            session: Optional aiohttp ClientSession for connection pooling
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._own_session = session is None
        self.syrcash = SyriatelCash(self)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._own_session = True
        return self._session
    
    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed and self._own_session:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _normalize_number(self, number: str) -> str:
        """Normalize phone number to 0XXXXXXXXX format"""
        number = number.replace(" ", "").replace("-", "")
        if number.startswith("+963"):
            number = "0" + number[4:]
        elif number.startswith("963"):
            number = "0" + number[3:]
        return number
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _filter_transactions_by_date(
        self,
        transactions: List[Transaction],
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Filter transactions by date range"""
        if not start_at and not end_at:
            return transactions
        
        filtered = []
        for tx in transactions:
            try:
                tx_date = self._parse_date(tx.date)
                
                if start_at:
                    start_dt = self._parse_date(start_at)
                    if tx_date < start_dt:
                        continue
                if end_at:
                    end_dt = self._parse_date(end_at)
                    if tx_date > end_dt:
                        continue
                
                filtered.append(tx)
            except ValueError:
                # Skip transactions with invalid dates
                continue
        
        return filtered
    
    async def _request(self, method: str, endpoint: str, params: Optional[dict] = None,
                       *, body: Optional[dict] = None, idempotency_key: Optional[str] = None):
        """Send one request. Purchases and throttled requests are never retried."""
        url = self.base_url[:-3] + endpoint if endpoint.startswith("/public/") and self.base_url.endswith("/v1") else f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"api-token": self.api_token, "Accept": "application/json"}
        if idempotency_key is not None:
            if not 8 <= len(idempotency_key) <= 128:
                raise ValueError("Use an Idempotency-Key of 8 to 128 characters")
            headers["Idempotency-Key"] = idempotency_key
        try:
            session = await self._get_session()
            kwargs = {"headers": headers, "params": params}
            if body is not None:
                kwargs["json"] = body
            async with session.request(method, url, **kwargs) as response:
                try:
                    payload = await response.json()
                except (ValueError, aiohttp.ContentTypeError):
                    payload = None
                retry = self._retry_after(response.headers.get("Retry-After", ""))
                if not isinstance(payload, dict):
                    if response.status == 429:
                        raise_error("RATE_LIMITED", retry_after=retry, status_code=429)
                    raise NetworkError("The API returned an invalid JSON response", code="NETWORK_ERROR", status_code=response.status)
                if response.status >= 400 or not payload.get("success", False):
                    error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
                    code = payload.get("code") or ("RATE_LIMITED" if response.status == 429 else "HTTP_ERROR")
                    raise_error(code, error.get("message"), payload.get("data"),
                                status_code=response.status, retry_after=retry,
                                request_id=error.get("request_id") or response.headers.get("X-Request-ID"))
                return payload.get("data")
        except SyriatelAPIError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise NetworkError("The API request could not be completed", code="NETWORK_ERROR") from exc

    @staticmethod
    def _retry_after(value: str) -> int:
        try:
            return max(0, int(value))
        except (ValueError, TypeError):
            try:
                when = parsedate_to_datetime(value)
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                return max(0, int((when - datetime.now(timezone.utc)).total_seconds()) + 1)
            except (ValueError, TypeError, OverflowError):
                return 0

    @staticmethod
    def _id(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("An account or link-session ID is required")
        return quote(value, safe="")

    async def get_public_plans(self) -> dict:
        return await self._request("GET", "/public/plans")

    async def get_service_status(self) -> dict:
        return await self._request("GET", "/public/status")

    async def get_profile(self) -> dict:
        return await self._request("GET", "/profile")

    async def get_plans(self) -> dict:
        return await self._request("GET", "/plans")

    async def list_accounts(self) -> list:
        """List every linked number, including unverified and expired numbers."""
        return (await self._request("GET", "/accounts"))["accounts"]

    async def get_account(self, account_id: str) -> dict:
        return await self._request("GET", "/accounts/" + self._id(account_id))

    async def rename_account(self, account_id: str, name: str) -> dict:
        return await self._request("PATCH", "/accounts/" + self._id(account_id), body={"name": name})

    async def remove_account(self, account_id: str) -> dict:
        return await self._request("DELETE", "/accounts/" + self._id(account_id))

    async def create_link_session(self, phone: str, password: str, *, idempotency_key: str) -> dict:
        return await self._request("POST", "/link-sessions", body={"phone": phone, "password": password}, idempotency_key=idempotency_key)

    async def get_link_session(self, session_id: str) -> dict:
        return await self._request("GET", "/link-sessions/" + self._id(session_id))

    async def verify_link_session(self, session_id: str, code: str) -> dict:
        if not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit():
            raise ValueError("The SMS code must be a six-digit string")
        return await self._request("POST", "/link-sessions/" + self._id(session_id) + "/verify", body={"code": code})

    async def cancel_link_session(self, session_id: str) -> dict:
        return await self._request("DELETE", "/link-sessions/" + self._id(session_id))

    async def verify_pin(self, account_id: str, pin: str) -> dict:
        if not isinstance(pin, str) or len(pin) != 4 or not pin.isascii() or not pin.isdigit():
            raise ValueError("PIN must be a four-digit string")
        return await self._request("POST", "/accounts/" + self._id(account_id) + "/pin", body={"pin": pin})

    async def start_trial(self, account_id: str, *, idempotency_key: str, auto_renew: Optional[bool] = None) -> dict:
        body = {} if auto_renew is None else {"auto_renew": auto_renew}
        return await self._request("POST", "/accounts/" + self._id(account_id) + "/trial", body=body, idempotency_key=idempotency_key)

    async def subscribe(self, account_id: str, *, idempotency_key: str, periods: int = 1,
                        plan_id: str = "monthly", auto_renew: Optional[bool] = None) -> dict:
        if type(periods) is not int or not 1 <= periods <= 12:
            raise ValueError("periods must be an integer from 1 to 12")
        body = {"plan_id": plan_id, "periods": periods}
        if auto_renew is not None:
            body["auto_renew"] = auto_renew
        return await self._request("POST", "/accounts/" + self._id(account_id) + "/subscription", body=body, idempotency_key=idempotency_key)

    async def get_subscription(self, account_id: str) -> dict:
        return await self._request("GET", "/accounts/" + self._id(account_id) + "/subscription")

    async def update_subscription(self, account_id: str, *, auto_renew: Optional[bool] = None, paused: Optional[bool] = None) -> dict:
        body = {key: value for key, value in {"auto_renew": auto_renew, "paused": paused}.items() if value is not None}
        if not body:
            raise ValueError("Set auto_renew or paused")
        return await self._request("PATCH", "/accounts/" + self._id(account_id) + "/subscription", body=body)

    async def disable_auto_renew(self, account_id: str) -> dict:
        return await self._request("DELETE", "/accounts/" + self._id(account_id) + "/subscription")

    async def get_balance(self, account_id: str) -> dict:
        """Read an active number's SYP balance without converting money to float."""
        return await self._request("GET", "/balances", params={"account_id": account_id})

    async def get_transactions(self, account_id: str, *, direction: str = "incoming", page: int = 1, search: str = "") -> dict:
        if direction not in {"incoming", "outgoing"}:
            raise ValueError("direction must be incoming or outgoing")
        if type(page) is not int or page < 1:
            raise ValueError("page must be a positive integer")
        return await self._request("GET", "/transactions", params={"account_id": account_id, "direction": direction, "page": page, "search": search})

    async def get_wallet(self, *, limit: int = 50, before_id: Optional[int] = None) -> dict:
        params = {"limit": limit}
        if before_id is not None:
            params["before_id"] = before_id
        return await self._request("GET", "/wallet", params=params)

    async def get_numbers(self) -> List[str]:
        """
        Get list of all active phone numbers
        
        Returns:
            List[str] - List of phone numbers
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [item.get("number", "") for item in data["numbers"] if item.get("number")]
    
    async def get_codes(self) -> List[str]:
        """
        Get list of all secret codes for active numbers
        
        Returns:
            List[str] - List of secret codes (may contain empty strings)
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [item.get("code", "") for item in data["numbers"] if item.get("code")]
    
    async def get_numbers_codes(self) -> List[Tuple[str, str]]:
        """
        Get list of all active numbers with their secret codes
        
        Returns:
            List[Tuple[str, str]] - List of (phone_number, secret_code) tuples
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
            
        Example:
            ```python
            numbers_codes = await api.get_numbers_codes()
            for number, code in numbers_codes:
                print(f"Number: {number}, Code: {code}")
            ```
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [
            (item.get("number", ""), item.get("code", ""))
            for item in data["numbers"]
            if item.get("number")
        ]


class SyriatelAPISync:
    """
    Synchronous client for Syriatel API
    
    This is a wrapper around the async client that provides sync methods.
    
    Example:
        ```python
        from syriatel import SyriatelAPISync
        
        api = SyriatelAPISync(api_token="your_token")
        numbers = api.get_numbers()
        balance = api.syrcash.balance("0991234567")
        ```
    """
    
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.melchersman.com/syr-cash/v1",
        timeout: int = 30,
    ):
        """
        Initialize the sync client
        
        Args:
            api_token: Your API token
            base_url: Base URL for the API (default: production URL)
            timeout: Request timeout in seconds (default: 30)
        """
        self._loop = asyncio.new_event_loop()
        self._async_client = SyriatelAPI(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
        )
        self.syrcash = SyriatelCashSync(
            self._async_client.syrcash,
            self._run_async
        )
    
    def _run_async(self, coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            coro.close()
            raise RuntimeError("Use SyriatelAPI inside an async application")
        if self._loop.is_closed():
            coro.close()
            raise RuntimeError("This client has been closed")
        return self._loop.run_until_complete(coro)

    def close(self):
        if not self._loop.is_closed():
            try:
                self._run_async(self._async_client.close())
            finally:
                self._loop.close()

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def get_numbers(self) -> List[str]:
        """Get list of all active phone numbers (sync)"""
        return self._run_async(self._async_client.get_numbers())
    
    def get_codes(self) -> List[str]:
        """Get list of all secret codes (sync)"""
        return self._run_async(self._async_client.get_codes())
    
    def get_numbers_codes(self) -> List[Tuple[str, str]]:
        """Get list of all active numbers with their secret codes (sync)"""
        return self._run_async(self._async_client.get_numbers_codes())

    def get_profile(self):
        return self._run_async(self._async_client.get_profile())

    def get_plans(self):
        return self._run_async(self._async_client.get_plans())

    def list_accounts(self):
        return self._run_async(self._async_client.list_accounts())

    def get_account(self, account_id: str):
        return self._run_async(self._async_client.get_account(account_id))

    def rename_account(self, account_id: str, name: str):
        return self._run_async(self._async_client.rename_account(account_id, name))

    def remove_account(self, account_id: str):
        return self._run_async(self._async_client.remove_account(account_id))

    def create_link_session(self, phone: str, password: str, *, idempotency_key: str):
        return self._run_async(self._async_client.create_link_session(phone, password, idempotency_key=idempotency_key))

    def get_link_session(self, session_id: str):
        return self._run_async(self._async_client.get_link_session(session_id))

    def verify_link_session(self, session_id: str, code: str):
        return self._run_async(self._async_client.verify_link_session(session_id, code))

    def cancel_link_session(self, session_id: str):
        return self._run_async(self._async_client.cancel_link_session(session_id))

    def verify_pin(self, account_id: str, pin: str):
        return self._run_async(self._async_client.verify_pin(account_id, pin))

    def start_trial(self, account_id: str, *, idempotency_key: str, auto_renew: Optional[bool]=None):
        return self._run_async(self._async_client.start_trial(account_id, idempotency_key=idempotency_key, auto_renew=auto_renew))

    def subscribe(self, account_id: str, *, idempotency_key: str, periods: int=1, plan_id: str='monthly', auto_renew: Optional[bool]=None):
        return self._run_async(self._async_client.subscribe(account_id, idempotency_key=idempotency_key, periods=periods, plan_id=plan_id, auto_renew=auto_renew))

    def get_subscription(self, account_id: str):
        return self._run_async(self._async_client.get_subscription(account_id))

    def update_subscription(self, account_id: str, *, auto_renew: Optional[bool]=None, paused: Optional[bool]=None):
        return self._run_async(self._async_client.update_subscription(account_id, auto_renew=auto_renew, paused=paused))

    def disable_auto_renew(self, account_id: str):
        return self._run_async(self._async_client.disable_auto_renew(account_id))

    def get_balance(self, account_id: str):
        return self._run_async(self._async_client.get_balance(account_id))

    def get_transactions(self, account_id: str, *, direction: str='incoming', page: int=1, search: str=''):
        return self._run_async(self._async_client.get_transactions(account_id, direction=direction, page=page, search=search))

    def get_wallet(self, *, limit: int=50, before_id: Optional[int]=None):
        return self._run_async(self._async_client.get_wallet(limit=limit, before_id=before_id))

    def get_public_plans(self):
        return self._run_async(self._async_client.get_public_plans())

    def get_service_status(self):
        return self._run_async(self._async_client.get_service_status())
