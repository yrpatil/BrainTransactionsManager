"""
Alpaca Market Adapter for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Unified Alpaca adapter supporting both stocks and crypto trading.
Simple, reliable implementation following SRM principles.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import re
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError
from functools import partial

from .base import MarketAdapter, AssetType, OrderSide, OrderType, OrderStatus
from ..core.exceptions import MarketAdapterError

logger = logging.getLogger(__name__)


class AlpacaAdapter(MarketAdapter):
    """
    Unified Alpaca adapter for stocks and crypto.
    
    Features:
    • Supports both stocks and crypto via single adapter
    • Automatic asset type detection
    • Unified order management
    • Error handling and retry logic
    • Simple and maintainable
    """
    
    def __init__(self, config, asset_types: List[AssetType] = None):
        """
        Initialize Alpaca adapter.
        
        Args:
            config: BrainConfig instance
            asset_types: Supported asset types (defaults to stocks and crypto)
        """
        if asset_types is None:
            asset_types = [AssetType.STOCK, AssetType.CRYPTO]
        
        super().__init__("alpaca_unified", asset_types)
        
        self.config = config
        self.asset_types = asset_types  # Store asset_types as instance variable
        self.api: Optional[tradeapi.REST] = None
        self.crypto_api: Optional[tradeapi.REST] = None
        
        # Asset type detection patterns
        self.crypto_patterns = ['USD', 'USDT', 'BTC', 'ETH']  # Common crypto suffixes
    
    @property
    def supported_asset_types(self) -> List[AssetType]:
        """Get supported asset types."""
        return self.asset_types
    
    async def connect(self) -> bool:
        """Connect to Alpaca API."""
        try:
            logger.info("🔄 Connecting to Alpaca API...")
            
            # Initialize stock trading API
            self.api = tradeapi.REST(
                self.config.alpaca.api_key,
                self.config.alpaca.secret_key,
                self.config.alpaca.base_url,
                api_version='v2'
            )
            
            # Test connection with account info
            account = await asyncio.get_event_loop().run_in_executor(
                None, self.api.get_account
            )
            logger.info(f"✅ Connected to Alpaca - Account: {account.status}")
            
            # Initialize crypto API (same credentials, different endpoints)
            self.crypto_api = self.api  # Alpaca uses same API for crypto
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Alpaca API."""
        try:
            self.api = None
            self.crypto_api = None
            self.is_connected = False
            logger.info("✅ Disconnected from Alpaca API")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Alpaca: {e}")
            return False
    
    def _detect_asset_type(self, symbol: str) -> AssetType:
        """
        Detect asset type from symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            AssetType: Detected asset type
        """
        symbol_upper = symbol.upper()
        
        # Check for crypto patterns
        for pattern in self.crypto_patterns:
            if pattern in symbol_upper:
                return AssetType.CRYPTO
        
        # Default to stock
        return AssetType.STOCK
    
    def _convert_order_status(self, alpaca_status: str) -> OrderStatus:
        """Convert Alpaca order status to internal status."""
        status_map = {
            'new': OrderStatus.PENDING,
            'accepted': OrderStatus.PENDING,
            'partially_filled': OrderStatus.PARTIALLY_FILLED,
            'filled': OrderStatus.FILLED,
            'done_for_day': OrderStatus.CANCELLED,
            'canceled': OrderStatus.CANCELLED,
            'expired': OrderStatus.CANCELLED,
            'replaced': OrderStatus.PENDING,
            'pending_cancel': OrderStatus.PENDING,
            'pending_replace': OrderStatus.PENDING,
            'accepted_for_bidding': OrderStatus.PENDING,
            'stopped': OrderStatus.CANCELLED,
            'rejected': OrderStatus.REJECTED,
            'suspended': OrderStatus.CANCELLED,
            'calculated': OrderStatus.PENDING
        }
        return status_map.get(alpaca_status, OrderStatus.PENDING)
    
    def _generate_client_order_id(self, symbol: str, strategy_name: str) -> str:
        """Generate a unique, debuggable client order id.
        
        Format: {env}-{strategy}-{symbol}-{uuid12}
        Ensures high uniqueness during batch operations like close-all.
        """
        env = getattr(self.config, 'environment', 'dev') or 'dev'
        safe_env = re.sub(r'[^a-zA-Z0-9_-]', '-', str(env))[:10]
        safe_strategy = re.sub(r'[^a-zA-Z0-9_-]', '-', str(strategy_name or 'default'))[:16]
        safe_symbol = re.sub(r'[^A-Z0-9_-]', '-', str(symbol).upper())[:12]
        unique = uuid.uuid4().hex[:12]
        return f"{safe_env}-{safe_strategy}-{safe_symbol}-{unique}"
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            account = await asyncio.get_event_loop().run_in_executor(
                None, self.api.get_account
            )
            
            return {
                'account_id': account.id,
                'status': account.status,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'day_trade_count': int(account.daytrade_count),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'account_blocked': account.account_blocked,
                'transfers_blocked': account.transfers_blocked
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise MarketAdapterError(f"Account info error: {e}")
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        strategy_name: str = "default"
    ) -> Dict[str, Any]:
        """Place a trading order."""
        try:
            asset_type = self._detect_asset_type(symbol)
            api_client = self.api  # Use same API for both stocks and crypto
            
            # Generate robust unique client order ID
            client_order_id = self._generate_client_order_id(symbol=symbol, strategy_name=strategy_name)
            
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'qty': quantity,
                'side': side.value,
                'type': order_type.value,
                'time_in_force': 'day',
                'client_order_id': client_order_id
            }
            
            # Add price for limit orders
            if order_type == OrderType.LIMIT and price:
                order_params['limit_price'] = price
            
            # Crypto-specific adjustments
            if asset_type == AssetType.CRYPTO:
                order_params['time_in_force'] = 'gtc'  # Crypto typically uses GTC
            
            # Try to submit order
            try:
                order = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: api_client.submit_order(**order_params)
                )
            except APIError as e:
                # Handle wash trade error by using complex orders
                if "wash trade" in str(e).lower():
                    logger.warning(f"Wash trade detected for {symbol}, using complex order")
                    
                    # Use complex order to avoid wash trade
                    complex_order_params = {
                        'symbol': symbol,
                        'qty': quantity,
                        'side': side.value,
                        'type': order_type.value,
                        'time_in_force': 'day',
                        'client_order_id': client_order_id,
                        'order_class': 'simple',  # Use simple order class
                        'take_profit': None,
                        'stop_loss': None
                    }
                    
                    if order_type == OrderType.LIMIT and price:
                        complex_order_params['limit_price'] = price
                    
                    if asset_type == AssetType.CRYPTO:
                        complex_order_params['time_in_force'] = 'gtc'
                    
                    order = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: api_client.submit_order(**complex_order_params)
                    )
                else:
                    # Re-raise if it's not a wash trade error
                    raise e
            
            logger.info(f"✅ Order placed: {order.id} - {side.value} {quantity} {symbol}")
            
            return {
                'order_id': order.id,
                'client_order_id': order.client_order_id,
                'symbol': order.symbol,
                'side': side.value,
                'quantity': float(order.qty),
                'order_type': order_type.value,
                'status': self._convert_order_status(order.status).value,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'asset_type': asset_type.value,
                'strategy_name': strategy_name
            }
            
        except APIError as e:
            logger.error(f"Alpaca API error placing order: {e}")
            raise MarketAdapterError(f"Order placement failed: {e}")
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise MarketAdapterError(f"Order placement error: {e}")
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.api.cancel_order, order_id
            )
            
            logger.info(f"✅ Order cancelled: {order_id}")
            
            return {
                'order_id': order_id,
                'status': 'cancelled',
                'cancelled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise MarketAdapterError(f"Order cancellation error: {e}")
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        try:
            order = await asyncio.get_event_loop().run_in_executor(
                None, self.api.get_order, order_id
            )
            
            return {
                'order_id': order.id,
                'client_order_id': order.client_order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': float(order.qty),
                'filled_quantity': float(order.filled_qty or 0),
                'status': self._convert_order_status(order.status).value,
                'order_type': order.order_type,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                'filled_avg_price': float(order.filled_avg_price or 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting order status {order_id}: {e}")
            raise MarketAdapterError(f"Order status error: {e}")
    
    async def get_positions(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current positions."""
        try:
            positions = await asyncio.get_event_loop().run_in_executor(
                None, self.api.list_positions
            )
            
            result = []
            for position in positions:
                if float(position.qty) != 0:  # Only include non-zero positions
                    asset_type = self._detect_asset_type(position.symbol)
                    
                    result.append({
                        'symbol': position.symbol,
                        'quantity': float(position.qty),
                        'side': 'long' if float(position.qty) > 0 else 'short',
                        'market_value': float(position.market_value or 0),
                        'cost_basis': float(position.cost_basis or 0),
                        'unrealized_pl': float(position.unrealized_pl or 0),
                        'unrealized_plpc': float(position.unrealized_plpc or 0),
                        'avg_entry_price': float(position.avg_entry_price or 0),
                        'asset_type': asset_type.value,
                        'strategy_name': strategy_name or 'default'  # We don't track strategy in Alpaca
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise MarketAdapterError(f"Positions error: {e}")
    
    async def get_orders(
        self,
        status: Optional[str] = None,
        strategy_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get orders."""
        try:
            # Convert status to Alpaca format
            # Default to pending orders if no status specified
            if status is None:
                status = 'pending'
                
            status_map = {
                'pending': 'new',
                'filled': 'filled',
                'cancelled': 'canceled',
                'rejected': 'rejected'
            }
            status_filter = status_map.get(status, status)
            
            orders = await asyncio.get_event_loop().run_in_executor(
                None, self.api.list_orders, status_filter
            )
            
            result = []
            for order in orders:
                asset_type = self._detect_asset_type(order.symbol)
                
                order_data = {
                    'order_id': order.id,
                    'client_order_id': order.client_order_id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': float(order.qty),
                    'filled_quantity': float(order.filled_qty or 0),
                    'status': self._convert_order_status(order.status).value,
                    'order_type': order.order_type,
                    'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                    'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                    'filled_avg_price': float(order.filled_avg_price or 0),
                    'asset_type': asset_type.value
                }
                
                # Filter by strategy if specified (extract from client_order_id)
                if strategy_name:
                    if order.client_order_id and strategy_name in order.client_order_id:
                        result.append(order_data)
                else:
                    result.append(order_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            raise MarketAdapterError(f"Orders error: {e}")
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data."""
        try:
            asset_type = self._detect_asset_type(symbol)
            
            if asset_type == AssetType.CRYPTO:
                # Get crypto market data using lambda for keyword arguments
                bars = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.api.get_crypto_bars(symbol, '1Day', limit=1)
                )
            else:
                # Get stock market data using lambda for keyword arguments
                bars = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.api.get_bars(symbol, '1Day', limit=1)
                )
            
            if bars and len(bars) > 0:
                bar = bars[0]
                return {
                    'symbol': symbol,
                    'price': float(bar.c),  # Close price
                    'open': float(bar.o),
                    'high': float(bar.h),
                    'low': float(bar.l),
                    'volume': int(bar.v),
                    'timestamp': bar.t.isoformat(),
                    'asset_type': asset_type.value
                }
            else:
                return {
                    'symbol': symbol,
                    'error': 'No market data available',
                    'asset_type': asset_type.value
                }
                
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'asset_type': self._detect_asset_type(symbol).value
            }
    
    async def get_supported_symbols(self) -> List[str]:
        """Get supported symbols."""
        try:
            # Get tradable assets using lambda for keyword arguments
            assets = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.api.list_assets(status='active', asset_class='us_equity')
            )
            
            symbols = [asset.symbol for asset in assets if asset.tradable]
            
            # Add common crypto symbols (Alpaca supports limited crypto)
            crypto_symbols = ['BTCUSD', 'ETHUSD', 'LTCUSD', 'BCHUSD']
            symbols.extend(crypto_symbols)
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting supported symbols: {e}")
            return []
    
    async def close_position(self, symbol: str, strategy_name: str = "default") -> Dict[str, Any]:
        """Close position for symbol."""
        try:
            # Get current position
            positions = await self.get_positions(strategy_name)
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                # If no position found, return success (nothing to close)
                logger.info(f"No position found for {symbol}, nothing to close")
                return {
                    'symbol': symbol,
                    'action': 'close',
                    'quantity': 0,
                    'side': 'none',
                    'order_id': None,
                    'message': 'No position to close'
                }
            
            # Place opposite order to close position
            side = OrderSide.SELL if position['side'] == 'long' else OrderSide.BUY
            quantity = abs(position['quantity'])
            
            logger.info(f"Closing position: {symbol} {position['side']} {quantity} shares")
            
            result = await self.place_order(
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=quantity,
                strategy_name=strategy_name
            )
            
            return {
                'symbol': symbol,
                'action': 'close',
                'quantity': quantity,
                'side': side.value,
                'order_id': result['order_id']
            }
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            raise MarketAdapterError(f"Close position error: {e}")
