"""
Adapter to expose Laxmi-yantra (Alpaca-backed) manager via the MarketAdapter interface.
"""

from typing import Dict, Any, Optional
from .base import MarketAdapter
from ..modules.laxmi_yantra.trading_manager import LaxmiYantra


class LaxmiYantraAdapter(MarketAdapter):
    def __init__(self):
        self.manager = LaxmiYantra()

    def buy(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market") -> Dict[str, Any]:
        return self.manager.buy(ticker, quantity, strategy_name, order_type)

    def sell(self, ticker: str, quantity: float, strategy_name: str = "default", order_type: str = "market") -> Dict[str, Any]:
        return self.manager.sell(ticker, quantity, strategy_name, order_type)

    def close_position(self, ticker: str, strategy_name: str = "default") -> Dict[str, Any]:
        return self.manager.close_position(ticker, strategy_name)

    def get_holdings(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        return self.manager.get_portfolio_summary(strategy_name)

    def poll_and_reconcile(self, strategy_name: str = "default", duration_seconds: int = 30, interval_seconds: float = 2.0) -> Dict[str, Any]:
        return self.manager.poll_and_reconcile(strategy_name, duration_seconds, interval_seconds)

    def supports_asset(self, ticker: str) -> bool:
        # Alpaca supports US equities and crypto under current setup; basic heuristic
        return True


