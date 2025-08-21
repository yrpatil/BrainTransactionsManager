"""
TradingFacade to route operations to the appropriate market adapter (US, Crypto, India, etc.).
Start simple: default adapter is Laxmi-yantra (Alpaca), pluggable in future.
"""

from typing import Dict, Any, Optional
from .base import MarketAdapter
from .laxmi_yantra_adapter import LaxmiYantraAdapter


class TradingFacade:
    def __init__(self, default_adapter: Optional[MarketAdapter] = None):
        self.default_adapter = default_adapter or LaxmiYantraAdapter()
        self.adapters: Dict[str, MarketAdapter] = {
            'default': self.default_adapter
        }

    def register_adapter(self, key: str, adapter: MarketAdapter) -> None:
        self.adapters[key] = adapter

    def _get_adapter(self, market: Optional[str]) -> MarketAdapter:
        if market and market in self.adapters:
            return self.adapters[market]
        return self.default_adapter

    def buy(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market", market: Optional[str] = None) -> Dict[str, Any]:
        return self._get_adapter(market).buy(ticker, quantity, strategy_name, order_type)

    def sell(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market", market: Optional[str] = None) -> Dict[str, Any]:
        return self._get_adapter(market).sell(ticker, quantity, strategy_name, order_type)

    def close_position(self, ticker: str, strategy_name: str = "default", market: Optional[str] = None) -> Dict[str, Any]:
        return self._get_adapter(market).close_position(ticker, strategy_name)

    def holdings(self, strategy_name: Optional[str] = None, market: Optional[str] = None) -> Dict[str, Any]:
        return self._get_adapter(market).get_holdings(strategy_name)

    def poll_and_reconcile(self, strategy_name: str = "default", duration_seconds: int = 30, interval_seconds: float = 2.0, market: Optional[str] = None) -> Dict[str, Any]:
        return self._get_adapter(market).poll_and_reconcile(strategy_name, duration_seconds, interval_seconds)


