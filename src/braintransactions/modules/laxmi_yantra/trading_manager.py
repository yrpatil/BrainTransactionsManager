"""
Laxmi-yantra Trading Manager - Main Trading Transaction Module
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Core trading transaction manager with Alpaca integration for order execution,
portfolio management, and real-time trading operations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit

from ...core.base_transaction import BaseTransactionManager
from ...core.config import BrainConfig
from ...core.exceptions import (
    TransactionExecutionError, 
    InvalidConfigurationError,
    InsufficientFundsError,
    OrderValidationError,
    APIConnectionError
)
from .portfolio_manager import PortfolioManager
from .order_manager import OrderManager

logger = logging.getLogger(__name__)

class LaxmiYantra(BaseTransactionManager):
    """
    🙏 Laxmi-yantra Trading Transaction Manager
    Blessed by Goddess Laxmi for Infinite Abundance
    
    Features:
    • Alpaca API integration for order execution
    • Real-time portfolio and position management
    • Kill switch support for emergency control
    • Transaction integrity and audit trails
    • Paper trading support for safe testing
    • Risk management and validation
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """
        Initialize Laxmi-yantra trading manager.
        
        Args:
            config: Configuration instance
        """
        logger.info("🙏 Initializing Laxmi-yantra Trading Manager - May Goddess Laxmi bless this system")
        super().__init__(config, "Laxmi-yantra")
        
        logger.info(f"✅ Laxmi-yantra initialized successfully in {'paper' if self.config.paper_trading else 'live'} trading mode")
    
    def _validate_module_configuration(self) -> None:
        """Validate Laxmi-yantra specific configuration."""
        # Check Alpaca credentials
        if not self.config.alpaca_api_key or not self.config.alpaca_secret_key:
            raise InvalidConfigurationError("Alpaca API credentials are required")
        
        # Validate Alpaca connection
        if not self.config.validate_alpaca_credentials():
            raise InvalidConfigurationError("Alpaca API credentials are invalid")
    
    def _initialize_components(self) -> None:
        """Initialize Laxmi-yantra components."""
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            self.config.alpaca_api_key,
            self.config.alpaca_secret_key,
            self.config.alpaca_base_url,
            api_version='v2'
        )
        
        # Initialize portfolio and order managers
        self.portfolio_manager = PortfolioManager(self.config)
        self.order_manager = OrderManager(self.config)
        
        # Trading state
        self.account_info = None
        self._refresh_account_info()
        
        logger.info("🔧 Laxmi-yantra components initialized successfully")
    
    def _refresh_account_info(self) -> None:
        """Refresh account information from Alpaca."""
        try:
            self.account_info = self.api.get_account()
            logger.debug(f"Account info refreshed - Status: {self.account_info.status}")
        except Exception as e:
            logger.error(f"Failed to refresh account info: {str(e)}")
            raise APIConnectionError(f"Failed to connect to Alpaca API: {str(e)}", "Alpaca")
    
    def _get_module_status(self) -> Dict[str, Any]:
        """Get Laxmi-yantra specific status."""
        try:
            self._refresh_account_info()
            
            return {
                'alpaca_connected': True,
                'account_status': self.account_info.status if self.account_info else 'unknown',
                'buying_power': float(self.account_info.buying_power) if self.account_info else 0.0,
                'cash': float(self.account_info.cash) if self.account_info else 0.0,
                'portfolio_value': float(self.account_info.portfolio_value) if self.account_info else 0.0,
                'paper_trading': self.config.paper_trading,
                'portfolio_manager_status': self.portfolio_manager.get_system_status() if hasattr(self, 'portfolio_manager') else {},
                'order_manager_status': self.order_manager.get_system_status() if hasattr(self, 'order_manager') else {}
            }
        except Exception as e:
            logger.error(f"Error getting module status: {str(e)}")
            return {
                'alpaca_connected': False,
                'error': str(e)
            }
    
    def _perform_module_health_checks(self) -> Dict[str, Dict[str, str]]:
        """Perform Laxmi-yantra specific health checks."""
        checks = {}
        
        # Alpaca API health check
        try:
            account = self.api.get_account()
            checks['alpaca_api'] = {
                'status': 'pass',
                'message': f'Connected - Account status: {account.status}'
            }
        except Exception as e:
            checks['alpaca_api'] = {
                'status': 'fail',
                'message': f'API connection failed: {str(e)}'
            }
        
        # Portfolio manager health check
        if hasattr(self, 'portfolio_manager'):
            portfolio_health = self.portfolio_manager.health_check()
            checks['portfolio_manager'] = {
                'status': 'pass' if portfolio_health['healthy'] else 'fail',
                'message': 'Portfolio manager is healthy' if portfolio_health['healthy'] else 'Portfolio manager issues detected'
            }
        
        # Order manager health check
        if hasattr(self, 'order_manager'):
            order_health = self.order_manager.health_check()
            checks['order_manager'] = {
                'status': 'pass' if order_health['healthy'] else 'fail',
                'message': 'Order manager is healthy' if order_health['healthy'] else 'Order manager issues detected'
            }
        
        return checks
    
    def _validate_transaction(self, transaction_data: Dict[str, Any]) -> None:
        """Validate trading transaction data."""
        required_fields = ['action', 'ticker', 'quantity']
        
        for field in required_fields:
            if field not in transaction_data:
                raise OrderValidationError(f"Missing required field: {field}")
        
        action = transaction_data['action'].lower()
        if action not in ['buy', 'sell']:
            raise OrderValidationError(f"Invalid action: {action}. Must be 'buy' or 'sell'")
        
        quantity = transaction_data['quantity']
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise OrderValidationError(f"Invalid quantity: {quantity}. Must be positive number")
        
        # Validate ticker format
        ticker = transaction_data['ticker']
        if not isinstance(ticker, str) or len(ticker) < 1:
            raise OrderValidationError(f"Invalid ticker: {ticker}")
        
        # Additional validation for sell orders
        if action == 'sell':
            strategy_name = transaction_data.get('strategy_name', 'default')
            current_position = self.portfolio_manager.get_position(strategy_name, ticker)
            
            if not current_position or current_position['quantity'] < quantity:
                available_qty = current_position['quantity'] if current_position else 0
                raise InsufficientFundsError(
                    f"Insufficient position to sell {quantity} shares of {ticker}",
                    required_amount=quantity,
                    available_amount=available_qty
                )
    
    def _execute_transaction_impl(self, transaction_data: Dict[str, Any], transaction_id: str) -> Dict[str, Any]:
        """Execute the actual trading transaction."""
        action = transaction_data['action'].lower()
        ticker = transaction_data['ticker']
        quantity = transaction_data['quantity']
        order_type = transaction_data.get('order_type', 'market')
        strategy_name = transaction_data.get('strategy_name', 'default')
        
        logger.info(f"🔄 Executing {action} order: {quantity} shares of {ticker}")
        
        try:
            # Place order through Alpaca
            order = self.api.submit_order(
                symbol=ticker,
                qty=quantity,
                side=action,
                type=order_type,
                time_in_force='day'
            )
            
            # Store order in database
            order_data = {
                'order_id': order.id,
                'client_order_id': order.client_order_id,
                'strategy_name': strategy_name,
                'ticker': ticker,
                'side': action,
                'order_type': order_type,
                'quantity': float(quantity),
                'price': float(order.limit_price) if order.limit_price else None,
                'status': order.status,
                'submitted_at': datetime.now(),
                'transaction_id': transaction_id
            }
            
            order_stored = self.order_manager.place_order(order_data)
            
            if not order_stored:
                logger.warning(f"Order placed with Alpaca but failed to store in database: {order.id}")
            
            # For market orders in paper trading, simulate immediate fill
            if self.config.paper_trading and order_type == 'market':
                # Get current price for simulation
                try:
                    bars = self.api.get_bars(ticker, TimeFrame(1, TimeFrameUnit.Minute), limit=1)
                    if bars.df.empty:
                        current_price = 100.0  # Fallback price for simulation
                    else:
                        current_price = float(bars.df.iloc[-1]['close'])
                    
                    # Update position in portfolio
                    if action == 'buy':
                        self.portfolio_manager.update_position(strategy_name, ticker, quantity, current_price)
                    else:  # sell
                        current_position = self.portfolio_manager.get_position(strategy_name, ticker)
                        new_quantity = current_position['quantity'] - quantity if current_position else 0
                        if new_quantity <= 0:
                            self.portfolio_manager.update_position(strategy_name, ticker, 0)
                        else:
                            self.portfolio_manager.update_position(strategy_name, ticker, new_quantity, current_position['avg_entry_price'])
                    
                    logger.info(f"📈 Position updated for paper trading: {strategy_name} {ticker}")
                    
                except Exception as e:
                    logger.warning(f"Could not simulate immediate fill: {str(e)}")
            
            return {
                'order_id': order.id,
                'client_order_id': order.client_order_id,
                'status': order.status,
                'quantity': float(quantity),
                'ticker': ticker,
                'action': action,
                'order_type': order_type,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'alpaca_order': {
                    'id': order.id,
                    'status': order.status,
                    'asset_class': order.asset_class,
                    'time_in_force': order.time_in_force
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to execute trading transaction: {str(e)}")
            raise TransactionExecutionError(
                f"Failed to place {action} order for {quantity} shares of {ticker}: {str(e)}",
                transaction_id=transaction_id,
                ticker=ticker
            )
    
    def buy(self, ticker: str, quantity: float, strategy_name: str = "default", 
            order_type: str = "market") -> Dict[str, Any]:
        """
        Execute a buy transaction.
        
        Args:
            ticker: Trading symbol
            quantity: Number of shares to buy
            strategy_name: Strategy identifier
            order_type: Order type (market, limit, etc.)
            
        Returns:
            Transaction result
        """
        transaction_data = {
            'action': 'buy',
            'ticker': ticker,
            'quantity': quantity,
            'strategy_name': strategy_name,
            'order_type': order_type
        }
        
        return self.execute_transaction(transaction_data)
    
    def sell(self, ticker: str, quantity: float, strategy_name: str = "default",
             order_type: str = "market") -> Dict[str, Any]:
        """
        Execute a sell transaction.
        
        Args:
            ticker: Trading symbol
            quantity: Number of shares to sell
            strategy_name: Strategy identifier
            order_type: Order type (market, limit, etc.)
            
        Returns:
            Transaction result
        """
        transaction_data = {
            'action': 'sell',
            'ticker': ticker,
            'quantity': quantity,
            'strategy_name': strategy_name,
            'order_type': order_type
        }
        
        return self.execute_transaction(transaction_data)
    
    def close_position(self, ticker: str, strategy_name: str = "default") -> Dict[str, Any]:
        """
        Close entire position for a ticker and strategy.
        
        Args:
            ticker: Trading symbol
            strategy_name: Strategy identifier
            
        Returns:
            Transaction result
        """
        position = self.portfolio_manager.get_position(strategy_name, ticker)
        
        if not position or position['quantity'] <= 0:
            return {
                'success': True,
                'message': f'No position to close for {strategy_name} {ticker}',
                'quantity_closed': 0
            }
        
        return self.sell(ticker, position['quantity'], strategy_name)
    
    def get_portfolio_summary(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio summary.
        
        Args:
            strategy_name: Filter by strategy (optional)
            
        Returns:
            Portfolio summary
        """
        return self.portfolio_manager.get_portfolio_summary(strategy_name)
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get current account information from Alpaca.
        
        Returns:
            Account information
        """
        try:
            self._refresh_account_info()
            
            if not self.account_info:
                return {'error': 'Account information not available'}
            
            return {
                'account_status': self.account_info.status,
                'buying_power': float(self.account_info.buying_power),
                'cash': float(self.account_info.cash),
                'portfolio_value': float(self.account_info.portfolio_value),
                'day_trade_buying_power': float(self.account_info.daytrading_buying_power),
                'equity': float(self.account_info.equity),
                'paper_trading': self.config.paper_trading,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {'error': str(e)}
    
    def emergency_stop(self, reason: str = "Emergency stop", 
                      stopped_by: Optional[str] = None) -> bool:
        """
        Emergency stop with position closure.
        
        Args:
            reason: Emergency stop reason
            stopped_by: Who initiated the emergency stop
            
        Returns:
            True if successful
        """
        logger.critical(f"🚨 Laxmi-yantra Emergency Stop Initiated: {reason}")
        
        try:
            # Close all positions
            positions = self.portfolio_manager.get_all_positions()
            
            for _, position in positions.iterrows():
                try:
                    if position['quantity'] > 0:
                        self.close_position(position['ticker'], position['strategy_name'])
                        logger.info(f"Emergency close: {position['strategy_name']} {position['ticker']}")
                except Exception as e:
                    logger.error(f"Failed to close position {position['ticker']}: {str(e)}")
            
            # Activate kill switch
            success = super().emergency_stop(reason, stopped_by)
            
            if success:
                logger.critical("🚨 Laxmi-yantra Emergency Stop Completed")
            
            return success
            
        except Exception as e:
            logger.critical(f"CRITICAL ERROR during Laxmi-yantra emergency stop: {str(e)}")
            return False
