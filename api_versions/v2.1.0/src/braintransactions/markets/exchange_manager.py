"""
Exchange Manager for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple exchange routing and management system.
Routes trading operations to appropriate market adapters.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base import MarketAdapter, AssetType, OrderSide, OrderType, OrderStatus
from .alpaca_adapter import AlpacaAdapter
from ..core.exceptions import MarketAdapterError
from ..core.logging_config import get_logger

logger = get_logger("exchange")


class ExchangeManager:
    """
    Simple exchange management system.
    
    Features:
    • Multi-exchange support
    • Automatic adapter selection
    • Asset type routing
    • Health monitoring
    • Unified trading interface
    • Kill switch support for emergency control
    """
    
    def __init__(self, config):
        """
        Initialize exchange manager.
        
        Args:
            config: BrainConfig instance
        """
        self.config = config
        self.adapters: Dict[str, MarketAdapter] = {}
        self.default_adapter: Optional[str] = None
        
        # Kill switch state
        self._kill_switch_active = False
        self._kill_switch_reason = None
        self._kill_switch_timestamp = None
        
        # Initialize adapters
        self._initialize_adapters()
    
    def activate_kill_switch(self, reason: str = "Kill switch activated"):
        """
        Activate kill switch to prevent all trading operations.
        
        Args:
            reason: Reason for activating kill switch
        """
        self._kill_switch_active = True
        self._kill_switch_reason = reason
        self._kill_switch_timestamp = datetime.now().isoformat()
        logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
    
    def deactivate_kill_switch(self):
        """Deactivate kill switch to resume trading operations."""
        self._kill_switch_active = False
        self._kill_switch_reason = None
        self._kill_switch_timestamp = None
        logger.success("Kill switch deactivated")
    
    def is_kill_switch_active(self) -> bool:
        """Check if kill switch is active."""
        return self._kill_switch_active
    
    def get_kill_switch_status(self) -> Dict[str, Any]:
        """Get kill switch status information."""
        return {
            'active': self._kill_switch_active,
            'reason': self._kill_switch_reason,
            'timestamp': self._kill_switch_timestamp
        }
    
    def _check_kill_switch(self, operation: str):
        """
        Check kill switch before performing operations.
        
        Args:
            operation: Operation being performed
            
        Raises:
            MarketAdapterError: If kill switch is active
        """
        if self._kill_switch_active:
            raise MarketAdapterError(
                f"Operation '{operation}' blocked by kill switch: {self._kill_switch_reason}"
            )
    
    def _initialize_adapters(self):
        """Initialize available market adapters."""
        try:
            # Initialize Alpaca adapter (supports both stocks and crypto)
            alpaca_adapter = AlpacaAdapter(self.config)
            self.register_adapter('alpaca', alpaca_adapter)
            
            # Set as default
            self.default_adapter = 'alpaca'
            
            logger.info(f"✅ Initialized {len(self.adapters)} market adapters")
            
        except Exception as e:
            logger.error(f"Failed to initialize adapters: {e}")
    
    def register_adapter(self, name: str, adapter: MarketAdapter):
        """
        Register a market adapter.
        
        Args:
            name: Adapter identifier
            adapter: MarketAdapter instance
        """
        self.adapters[name] = adapter
        logger.info(f"📝 Registered adapter: {name} ({adapter.name})")
    
    def get_adapter(self, exchange: Optional[str] = None, asset_type: Optional[AssetType] = None) -> MarketAdapter:
        """
        Get appropriate market adapter.
        
        Args:
            exchange: Specific exchange name (optional)
            asset_type: Asset type for automatic selection (optional)
            
        Returns:
            MarketAdapter instance
        """
        # Check kill switch
        self._check_kill_switch("adapter selection")
        
        # If specific exchange requested
        if exchange and exchange in self.adapters:
            adapter = self.adapters[exchange]
            if asset_type and not adapter.supports_asset_type(asset_type):
                raise MarketAdapterError(f"Adapter {exchange} doesn't support {asset_type.value}")
            return adapter
        
        # Auto-select based on asset type
        if asset_type:
            for adapter in self.adapters.values():
                if adapter.supports_asset_type(asset_type):
                    return adapter
            raise MarketAdapterError(f"No adapter supports {asset_type.value}")
        
        # Use default adapter
        if self.default_adapter and self.default_adapter in self.adapters:
            return self.adapters[self.default_adapter]
        
        raise MarketAdapterError("No adapters available")
    
    async def connect_all(self) -> bool:
        """Connect to all registered exchanges."""
        try:
            self._check_kill_switch("connect all")
            
            success_count = 0
            for name, adapter in self.adapters.items():
                try:
                    if await adapter.connect():
                        success_count += 1
                        logger.info(f"✅ Connected to {name}")
                    else:
                        logger.error(f"❌ Failed to connect to {name}")
                except Exception as e:
                    logger.error(f"❌ Error connecting to {name}: {e}")
            
            logger.info(f"📊 Connected to {success_count}/{len(self.adapters)} exchanges")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Connect all error: {e}")
            return False
    
    async def disconnect_all(self):
        """Disconnect from all exchanges."""
        try:
            for name, adapter in self.adapters.items():
                try:
                    await adapter.disconnect()
                    logger.info(f"✅ Disconnected from {name}")
                except Exception as e:
                    logger.error(f"❌ Error disconnecting from {name}: {e}")
        except Exception as e:
            logger.error(f"Disconnect all error: {e}")
    
    async def place_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                         quantity: float, price: Optional[float] = None,
                         strategy_name: str = "default", exchange: Optional[str] = None) -> Dict[str, Any]:
        """Place a trading order."""
        self._check_kill_switch("place order")
        
        # Detect asset type from symbol
        asset_type = self._detect_asset_type(symbol)
        adapter = self.get_adapter(exchange, asset_type)
        
        return await adapter.place_order(symbol, side, order_type, quantity, price, strategy_name)
    
    async def cancel_order(self, order_id: str, exchange: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an order."""
        self._check_kill_switch("cancel order")
        
        # Try to find the order first to determine asset type
        adapter = self.get_adapter(exchange)
        return await adapter.cancel_order(order_id)
    
    async def get_order_status(self, order_id: str, exchange: Optional[str] = None) -> Dict[str, Any]:
        """Get order status."""
        adapter = self.get_adapter(exchange)
        return await adapter.get_order_status(order_id)
    
    async def get_orders(self, status: Optional[str] = None, strategy_name: Optional[str] = None,
                        exchange: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders."""
        adapter = self.get_adapter(exchange)
        return await adapter.get_orders(status, strategy_name)
    
    async def get_positions(self, strategy_name: Optional[str] = None,
                           exchange: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current positions."""
        adapter = self.get_adapter(exchange)
        return await adapter.get_positions(strategy_name)
    
    async def get_account_info(self, exchange: Optional[str] = None) -> Dict[str, Any]:
        """Get account information."""
        adapter = self.get_adapter(exchange)
        return await adapter.get_account_info()
    
    async def get_market_data(self, symbol: str, exchange: Optional[str] = None) -> Dict[str, Any]:
        """Get market data for symbol."""
        asset_type = self._detect_asset_type(symbol)
        adapter = self.get_adapter(exchange, asset_type)
        return await adapter.get_market_data(symbol)
    
    async def close_position(self, symbol: str, strategy_name: str = "default",
                            exchange: Optional[str] = None) -> Dict[str, Any]:
        """Close position for symbol."""
        self._check_kill_switch("close position")
        
        asset_type = self._detect_asset_type(symbol)
        adapter = self.get_adapter(exchange, asset_type)
        return await adapter.close_position(symbol, strategy_name)
    
    def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges."""
        return list(self.adapters.keys())
    
    def get_adapter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all adapters."""
        info = {}
        for name, adapter in self.adapters.items():
            info[name] = {
                'name': adapter.name,
                'supported_assets': [asset.value for asset in adapter.supported_asset_types],
                'is_connected': adapter.is_connected,
                'is_default': name == self.default_adapter
            }
        return info
    
    def _detect_asset_type(self, symbol: str) -> AssetType:
        """Detect asset type from symbol."""
        symbol_upper = symbol.upper()
        
        # Crypto patterns
        crypto_patterns = ['USD', 'USDT', 'BTC', 'ETH', '/']
        for pattern in crypto_patterns:
            if pattern in symbol_upper:
                return AssetType.CRYPTO
        
        # Default to stock
        return AssetType.STOCK
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all adapters."""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'adapters': {},
                'total_adapters': len(self.adapters),
                'healthy_adapters': 0
            }
            
            for name, adapter in self.adapters.items():
                try:
                    # Basic health check
                    is_healthy = adapter.is_connected
                    health_data['adapters'][name] = {
                        'status': 'healthy' if is_healthy else 'unhealthy',
                        'adapter': adapter.name,
                        'supported_assets': [asset.value for asset in adapter.supported_asset_types],
                        'account_status': 'ACTIVE' if is_healthy else 'UNKNOWN'
                    }
                    
                    if is_healthy:
                        health_data['healthy_adapters'] += 1
                        
                except Exception as e:
                    health_data['adapters'][name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            return health_data
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'adapters': {},
                'total_adapters': 0,
                'healthy_adapters': 0
            }
