"""Synchronous and asynchronous clients for the Syriatel Cash platform."""

from .client import SyriatelAPI, SyriatelAPISync, SyriatelCash
from .models import Transaction
from .v2 import SyriatelV2,SyriatelV2Sync
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

__version__ = "2.3.1"
__all__ = [
    "SyriatelV2",
    "SyriatelV2Sync",
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
