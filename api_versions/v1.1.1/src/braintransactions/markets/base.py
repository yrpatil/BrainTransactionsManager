"""
Market adapter interfaces for multi-market support (US equities, Crypto, India, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class MarketAdapter(ABC):
    """Abstract interface for market adapters used by the trading facade."""

    @abstractmethod
    def buy(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market") -> Dict[str, Any]:
        pass

    @abstractmethod
    def sell(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market") -> Dict[str, Any]:
        pass

    @abstractmethod
    def close_position(self, ticker: str, strategy_name: str = "default") -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_holdings(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def poll_and_reconcile(self, strategy_name: str = "default", duration_seconds: int = 30, interval_seconds: float = 2.0) -> Dict[str, Any]:
        pass

    @abstractmethod
    def supports_asset(self, ticker: str) -> bool:
        pass


