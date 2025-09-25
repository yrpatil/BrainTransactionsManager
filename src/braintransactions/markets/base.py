"""
Base Market Adapter for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, extensible base class for market adapters.
Supports multiple exchanges and asset types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Supported asset types."""
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"  # Future support
    OPTION = "option"  # Future support


class OrderSide(Enum):
    """Order sides."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Order statuses."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class MarketAdapter(ABC):
    """
    Base class for all market adapters.
    
    Defines the standard interface for trading operations
    across different exchanges and asset types.
    """
    
    def __init__(self, name: str, supported_assets: List[AssetType]):
        """
        Initialize market adapter.
        
        Args:
            name: Adapter name (e.g., "alpaca_stocks", "alpaca_crypto")
            supported_assets: List of supported asset types
        """
        self.name = name
        self.supported_assets = supported_assets
        self.is_connected = False
        logger.info(f"🔄 Initializing {name} adapter for {[a.value for a in supported_assets]}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the exchange/broker.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the exchange/broker.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account information dictionary
        """
        pass
    
    @abstractmethod
    async def place_order(self, 
                         symbol: str,
                         side: OrderSide,
                         order_type: OrderType,
                         quantity: float,
                         price: Optional[float] = None,
                         strategy_name: str = "default") -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            symbol: Trading symbol (e.g., "AAPL", "BTCUSD")
            side: Order side (buy/sell)
            order_type: Order type (market/limit/etc)
            quantity: Order quantity
            price: Order price (for limit orders)
            strategy_name: Strategy identifier
            
        Returns:
            Order confirmation dictionary
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation confirmation dictionary
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order status dictionary
        """
        pass
    
    @abstractmethod
    async def get_positions(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Args:
            strategy_name: Filter by strategy (optional)
            
        Returns:
            List of position dictionaries
        """
        pass
    
    @abstractmethod
    async def get_orders(self, 
                        status: Optional[OrderStatus] = None,
                        strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders.
        
        Args:
            status: Filter by order status (optional)
            strategy_name: Filter by strategy (optional)
            
        Returns:
            List of order dictionaries
        """
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Market data dictionary
        """
        pass
    
    @abstractmethod
    async def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported trading symbols.
        
        Returns:
            List of supported symbols
        """
        pass
    
    def supports_asset_type(self, asset_type: AssetType) -> bool:
        """
        Check if adapter supports asset type.
        
        Args:
            asset_type: Asset type to check
            
        Returns:
            True if supported
        """
        return asset_type in self.supported_assets
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status dictionary
        """
        try:
            if not self.is_connected:
                return {
                    'status': 'disconnected',
                    'adapter': self.name,
                    'supported_assets': [a.value for a in self.supported_assets]
                }
            
            # Test with account info call
            account = await self.get_account_info()
            
            return {
                'status': 'healthy',
                'adapter': self.name,
                'supported_assets': [a.value for a in self.supported_assets],
                'account_status': account.get('status', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return {
                'status': 'unhealthy',
                'adapter': self.name,
                'error': str(e)
            }
    
    # Convenience methods for common operations
    async def buy(self, symbol: str, quantity: float, strategy_name: str = "default", 
                  order_type: OrderType = OrderType.MARKET, price: Optional[float] = None) -> Dict[str, Any]:
        """Convenience method for buy orders."""
        return await self.place_order(symbol, OrderSide.BUY, order_type, quantity, price, strategy_name)
    
    async def sell(self, symbol: str, quantity: float, strategy_name: str = "default",
                   order_type: OrderType = OrderType.MARKET, price: Optional[float] = None) -> Dict[str, Any]:
        """Convenience method for sell orders."""
        return await self.place_order(symbol, OrderSide.SELL, order_type, quantity, price, strategy_name)
    
    async def close_position(self, symbol: str, strategy_name: str = "default") -> Dict[str, Any]:
        """
        Close entire position for a symbol.
        
        Args:
            symbol: Symbol to close
            strategy_name: Strategy identifier
            
        Returns:
            Order confirmation dictionary
        """
        positions = await self.get_positions(strategy_name)
        
        for position in positions:
            if position.get('symbol') == symbol:
                quantity = abs(float(position.get('quantity', 0)))
                if quantity > 0:
                    # Determine side based on current position
                    current_qty = float(position.get('quantity', 0))
                    side = OrderSide.SELL if current_qty > 0 else OrderSide.BUY
                    
                    return await self.place_order(
                        symbol, side, OrderType.MARKET, quantity, None, strategy_name
                    )
        
        return {'status': 'no_position', 'symbol': symbol}
