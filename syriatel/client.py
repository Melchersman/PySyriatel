"""
Syriatel API Client

Supports both async and sync operations.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, List, Tuple
from .exceptions import raise_error, NetworkError
from .models import Transaction


class SyriatelCash:
    """
    Syriatel Cash API namespace
    
    Contains methods for interacting with Syriatel Cash services.
    """
    
    def __init__(self, api: "SyriatelAPI"):
        """Initialize the Cash namespace with API client"""
        self._api = api
    
    async def balance(self, number: Optional[str] = None, code: Optional[str] = None) -> int:
        """
        Get Syriatel Cash balance for a phone number or secret code
        
        Args:
            number: Phone number in format 0XXXXXXXXX (will be normalized, required if code not provided)
            code: Secret code (required if number not provided)
            
        Returns:
            Balance as integer (in SYP)
            
        Raises:
            ValueError: If neither number nor code is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            ServerMaintenanceError: If servers are under maintenance
            NetworkError: If network request fails
        """
        if not number and not code:
            raise ValueError("Either 'number' or 'code' must be provided")
        params = {}
        if number:
            params["number"] = self._api._normalize_number(number)
        elif code:
            params["code"] = code
        data = await self._api._request("GET", "/Balance", params=params)
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
        Find an incoming transaction by transaction number.
        
        Returns:
            Transaction: If found.
            None: If searched successfully but not found.
        
        Raises:
            NetworkError, InvalidTokenError, etc.: Propagates errors from get_incoming_history
            so the caller knows the search failed due to technical issues.
        """
        if not number and not code:
            raise ValueError("Either 'number' or 'code' must be provided")
        for page in range(1, max_pages + 1):
            transactions = await self.get_incoming_history(number, code, page)
            tx = self.find_transaction_by_number(transactions, transaction_no)
            if tx:
                return tx
            if len(transactions) == 0:
                return None
        return None


class SyriatelCashSync:
    """Sync wrapper for SyriatelCash namespace"""
    
    def __init__(self, async_cash: SyriatelCash, run_async_func):
        self._async_cash = async_cash
        self._run_async = run_async_func
    
    def balance(self, number: Optional[str] = None, code: Optional[str] = None) -> int:
        """Get balance (sync)"""
        return self._run_async(self._async_cash.balance(number, code))
    
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
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make an async HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            Response data dictionary
            
        Raises:
            NetworkError: If network request fails
            Various API errors based on response code
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"api-token": self.api_token}
        
        try:
            session = await self._get_session()
            async with session.request(
                method, url, headers=headers, params=params
            ) as response:
                try:
                    data = await response.json()
                except Exception:
                    raise NetworkError(
                        f"Invalid JSON response: {response.status}",
                        code="NETWORK_ERROR",
                    )
                
                if not data.get("success", False):
                    code = data.get("code", "UNKNOWN_ERROR")
                    raise_error(code, data=data.get("data"))
                
                return data.get("data", {})
        except aiohttp.ClientError as e:
            raise NetworkError(
                f"Network request failed: {str(e)}",
                code="NETWORK_ERROR",
            )
        except Exception as e:
            # Re-raise if it's already a SyriatelAPIError
            if isinstance(e, (NetworkError,)):
                raise
            # Otherwise wrap it
            raise NetworkError(
                f"Unexpected error: {str(e)}",
                code="NETWORK_ERROR",
            )
    
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
        """Run async coroutine in sync context"""
        try:
            # Check if we're already in an async context
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync client inside async context. Use SyriatelAPI instead."
            )
        except RuntimeError as e:
            if "Cannot use sync client" in str(e):
                raise
            # No running loop, safe to create one
            pass
        
        # Create or get event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def close(self):
        """Close the client"""
        if self._async_client:
            self._run_async(self._async_client.close())
    
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
