"""
Data models for Syriatel Cash API responses
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a transaction in the history"""
    transaction_no: str
    date: str
    from_gsm: str
    to_gsm: str
    amount: int
    fee: int
    net: int
    channel: str
    status: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create Transaction from API response dict"""
        return cls(
            transaction_no=data.get("transaction_no", ""),
            date=data.get("date", ""),
            from_gsm=data.get("from_gsm", ""),
            to_gsm=data.get("to_gsm", ""),
            amount=int(data.get("amount", 0)),
            fee=int(data.get("fee", 0)),
            net=int(data.get("net", 0)),
            channel=data.get("channel", ""),
            status=data.get("status", ""),
        )


@dataclass
class HistoryResponse:
    """Represents a history response"""
    total: int
    transactions: List[Transaction]
    
    @classmethod
    def from_dict(cls, data: dict) -> "HistoryResponse":
        """Create HistoryResponse from API response dict"""
        transactions = [
            Transaction.from_dict(tx) for tx in data.get("transactions", [])
        ]
        return cls(
            total=int(data.get("total", 0)),
            transactions=transactions,
        )


@dataclass
class NumberWithCode:
    """Represents a phone number with its secret code"""
    number: str
    code: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "NumberWithCode":
        """Create NumberWithCode from API response dict"""
        return cls(
            number=data.get("number", ""),
            code=data.get("code", ""),
        )


@dataclass
class BalanceResponse:
    """Represents a balance response"""
    balance: int
    
    @classmethod
    def from_dict(cls, data: dict) -> "BalanceResponse":
        """Create BalanceResponse from API response dict"""
        return cls(balance=int(data.get("balance", 0)))

