"""
Custom exceptions for Syriatel API
"""


class SyriatelAPIError(Exception):
    """Base exception for all Syriatel API errors"""
    
    def __init__(self, message: str, code: str = None, data: dict = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class InvalidTokenError(SyriatelAPIError):
    """API token is missing or invalid"""
    pass


class SubscriptionExpiredError(SyriatelAPIError):
    """No active subscription for the requested number"""
    pass


class FetchFailedError(SyriatelAPIError):
    """Failed to fetch data from Syriatel servers"""
    pass


class NotAuthorizedError(SyriatelAPIError):
    """Account authorization issue"""
    pass


class ServerMaintenanceError(SyriatelAPIError):
    """Syriatel servers are under maintenance"""
    pass


class NetworkError(SyriatelAPIError):
    """Network connectivity issue"""
    pass


class GSMNotFoundError(SyriatelAPIError):
    """Phone number not found in system"""
    pass


class VerificationRequiredError(SyriatelAPIError):
    """Additional verification step required"""
    pass


class VerificationFailedError(SyriatelAPIError):
    """Verification code/process failed"""
    pass


class PINInvalidError(SyriatelAPIError):
    """PIN code is incorrect"""
    pass


class LoginFailedError(SyriatelAPIError):
    """Login attempt failed"""
    pass


# Error code to exception mapping
ERROR_MAP = {
    "INVALID_TOKEN": InvalidTokenError,
    "NO_TOKEN": InvalidTokenError,
    "SUBSCRIPTION_EXPIRED": SubscriptionExpiredError,
    "FETCH_FAILED": FetchFailedError,
    "NOT_AUTHORIZED": NotAuthorizedError,
    "SERVER_MAINTENANCE": ServerMaintenanceError,
    "NETWORK_ERROR": NetworkError,
    "GSM_NOT_FOUND": GSMNotFoundError,
    "VERIFICATION_REQUIRED": VerificationRequiredError,
    "VERIFICATION_FAILED": VerificationFailedError,
    "PIN_INVALID": PINInvalidError,
    "LOGIN_FAILED": LoginFailedError,
}


def raise_error(code: str, message: str = None, data: dict = None):
    """Raise appropriate exception based on error code"""
    exception_class = ERROR_MAP.get(code, SyriatelAPIError)
    error_message = message or f"API error: {code}"
    raise exception_class(error_message, code=code, data=data)
