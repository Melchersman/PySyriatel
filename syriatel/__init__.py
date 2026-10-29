"""Synchronous and asynchronous clients for the Syriatel Cash platform."""

from .client import SyriatelAPI, SyriatelAPISync, SyriatelCash
from .models import Transaction
from .exceptions import (
    SyriatelAPIError,
    RateLimitError,
    ManagementDisabledError,
    InsufficientBalanceError,
    IdempotencyConflictError,
    InvalidTokenError,
    SubscriptionExpiredError,
    FetchFailedError,
    NotAuthorizedError,
    ServerMaintenanceError,
    NetworkError,
    GSMNotFoundError,
    VerificationRequiredError,
    VerificationFailedError,
    PINInvalidError,
    LoginFailedError,
)

__version__ = "2.2.0"
__all__ = [
    "SyriatelAPI",
    "SyriatelAPISync",
    "SyriatelCash",
    "Transaction",
    "SyriatelAPIError",
    "RateLimitError",
    "ManagementDisabledError",
    "InsufficientBalanceError",
    "IdempotencyConflictError",
    "InvalidTokenError",
    "SubscriptionExpiredError",
    "FetchFailedError",
    "NotAuthorizedError",
    "ServerMaintenanceError",
    "NetworkError",
    "GSMNotFoundError",
    "VerificationRequiredError",
    "VerificationFailedError",
    "PINInvalidError",
    "LoginFailedError",
]
