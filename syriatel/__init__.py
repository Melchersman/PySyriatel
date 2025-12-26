"""
Syriatel API Python Library

A professional Python library for interacting with the Syriatel API.
Supports both async and sync operations.
"""

from .client import SyriatelAPI, SyriatelAPISync, SyriatelCash
from .models import Transaction
from .exceptions import (
    SyriatelAPIError,
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

__version__ = "2.0.0"
__all__ = [
    "SyriatelAPI",
    "SyriatelAPISync",
    "SyriatelCash",
    "Transaction",
    "SyriatelAPIError",
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
