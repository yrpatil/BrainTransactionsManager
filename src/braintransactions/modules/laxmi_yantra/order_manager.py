"""
Order Manager for Laxmi-yantra Trading Module
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Order execution and management with database persistence and kill switch support.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from ...database import DatabaseManager
from ...core.kill_switch import KillSwitchMixin
from ...core.config import BrainConfig

logger = logging.getLogger(__name__)

class OrderManager(KillSwitchMixin):
    """
    Simple, reliable, and maintainable order management for Laxmi-yantra.
    
    Features:
    • Place new order (insert)
    • Update order status/fields
    • Get order(s) by ID, strategy, ticker, status, or time range
    • List all orders (with filters)
    • Kill switch support for all writes
    • Ready for Telegram/live integration
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """Initialize Order Manager."""
        super().__init__()  # Initialize KillSwitchMixin
        
        self.config = config or BrainConfig()
        self.db = DatabaseManager(self.config)
        
        logger.info("🙏 Laxmi-yantra Order Manager initialized")
        
        # Ensure database tables exist
        self.db.create_tables()

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for monitoring."""
        try:
            db_status = self.db.check_connection()
            return {
                'kill_switch_active': self.is_kill_switch_active(),
                'database_connected': db_status,
                'timestamp': datetime.now().isoformat(),
                'system_ready': not self.is_kill_switch_active() and db_status
            }
        except Exception as e:
            logger.error(f"Order system status error: {str(e)}")
            return {
                'kill_switch_active': self.is_kill_switch_active(),
                'database_connected': False,
                'timestamp': datetime.now().isoformat(),
                'system_ready': False,
                'error': str(e)
            }

    def place_order(self, order: Dict[str, Any]) -> bool:
        """
        Place a new order. Order dict must include:
        - order_id, strategy_name, ticker, order_type, side, quantity, price (optional), status
        """
        self.check_kill_switch_and_raise("order placement")
        
        try:
            query = """
                INSERT INTO order_history (
                    order_id, client_order_id, strategy_name, ticker, order_type, side, quantity, 
                    price, status, filled_quantity, filled_avg_price, commission, submitted_at, notes
                ) VALUES (
                    %(order_id)s, %(client_order_id)s, %(strategy_name)s, %(ticker)s, %(order_type)s, %(side)s, %(quantity)s,
                    %(price)s, %(status)s, %(filled_quantity)s, %(filled_avg_price)s, %(commission)s, %(submitted_at)s, %(notes)s
                )
                ON CONFLICT (order_id) DO NOTHING
            """
            self.db.execute_action(query, {
                'order_id': order['order_id'],
                'client_order_id': order.get('client_order_id'),
                'strategy_name': order['strategy_name'],
                'ticker': order['ticker'],
                'order_type': order['order_type'],
                'side': order['side'],
                'quantity': order['quantity'],
                'price': order.get('price'),
                'status': order['status'],
                'filled_quantity': order.get('filled_quantity', 0),
                'filled_avg_price': order.get('filled_avg_price'),
                'commission': order.get('commission', 0),
                'submitted_at': order.get('submitted_at', datetime.now()),
                'notes': order.get('notes')
            })
            logger.info(f"Order placed: {order['order_id']} {order['strategy_name']} {order['ticker']}")
            return True
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return False

    def update_order_status(self, order_id: str, status: str, 
                           filled_quantity: Optional[float] = None, 
                           filled_avg_price: Optional[float] = None, 
                           commission: Optional[float] = None, 
                           notes: Optional[str] = None) -> bool:
        """
        Update order status and optionally filled quantity/price/commission/notes.
        """
        self.check_kill_switch_and_raise("order status update")
        
        try:
            query = """
                UPDATE order_history
                SET status = %(status)s,
                    filled_quantity = COALESCE(%(filled_quantity)s, filled_quantity),
                    filled_avg_price = COALESCE(%(filled_avg_price)s, filled_avg_price),
                    commission = COALESCE(%(commission)s, commission),
                    notes = COALESCE(%(notes)s, notes),
                    filled_at = CASE WHEN %(status)s = 'filled' THEN CURRENT_TIMESTAMP ELSE filled_at END
                WHERE order_id = %(order_id)s
            """
            self.db.execute_action(query, {
                'order_id': order_id,
                'status': status,
                'filled_quantity': filled_quantity,
                'filled_avg_price': filled_avg_price,
                'commission': commission,
                'notes': notes
            })
            logger.info(f"Order updated: {order_id} status={status}")
            return True
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            return False

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific order by ID."""
        try:
            query = """
                SELECT * FROM order_history WHERE order_id = %(order_id)s
            """
            return self.db.execute_single(query, {'order_id': order_id})
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            return None

    def get_orders(self, strategy_name: Optional[str] = None, 
                   ticker: Optional[str] = None, 
                   status: Optional[str] = None, 
                   start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None,
                   limit: int = 100) -> pd.DataFrame:
        """Get orders with optional filters."""
        try:
            query = "SELECT * FROM order_history WHERE 1=1"
            params = {}
            
            if strategy_name:
                query += " AND strategy_name = %(strategy_name)s"
                params['strategy_name'] = strategy_name
            if ticker:
                query += " AND ticker = %(ticker)s"
                params['ticker'] = ticker
            if status:
                query += " AND status = %(status)s"
                params['status'] = status
            if start_time:
                query += " AND submitted_at >= %(start_time)s"
                params['start_time'] = start_time
            if end_time:
                query += " AND submitted_at <= %(end_time)s"
                params['end_time'] = end_time
            
            query += " ORDER BY submitted_at DESC LIMIT %(limit)s"
            params['limit'] = limit
            
            results = self.db.execute_query(query, params)
            return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return pd.DataFrame()

    def get_open_orders(self, strategy_name: Optional[str] = None) -> pd.DataFrame:
        """Get all pending/open orders."""
        return self.get_orders(strategy_name=strategy_name, status='pending')

    def get_filled_orders(self, strategy_name: Optional[str] = None) -> pd.DataFrame:
        """Get all filled orders."""
        return self.get_orders(strategy_name=strategy_name, status='filled')

    def cancel_order(self, order_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel an order (set status to 'cancelled').
        """
        return self.update_order_status(order_id, status='cancelled', notes=reason)
    
    def get_order_history(self, strategy_name: Optional[str] = None, 
                         ticker: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Get order history with optional filters.
        
        Args:
            strategy_name: Filter by strategy (optional)
            ticker: Filter by ticker (optional)
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with order history
        """
        try:
            query = """
                SELECT order_id, client_order_id, strategy_name, ticker, side, 
                       order_type, quantity, filled_quantity, price, filled_avg_price,
                       status, submitted_at, filled_at, canceled_at, created_at
                FROM order_history
                WHERE 1=1
            """
            params = {}
            
            if strategy_name:
                query += " AND strategy_name = %(strategy_name)s"
                params['strategy_name'] = strategy_name
            
            if ticker:
                query += " AND ticker = %(ticker)s"
                params['ticker'] = ticker
            
            query += " ORDER BY submitted_at DESC LIMIT %(limit)s"
            params['limit'] = limit
            
            results = self.db.execute_query(query, params)
            
            if results:
                df = pd.DataFrame(results)
                df['submitted_at'] = pd.to_datetime(df['submitted_at'])
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            return pd.DataFrame()
    
    def get_order_statistics(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get order statistics and performance metrics.
        
        Args:
            strategy_name: Filter by strategy (optional)
            
        Returns:
            Dictionary with order statistics
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'filled' THEN 1 END) as filled_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    SUM(CASE WHEN status = 'filled' THEN quantity ELSE 0 END) as total_filled_quantity,
                    AVG(CASE WHEN status = 'filled' THEN filled_avg_price END) as avg_fill_price,
                    SUM(CASE WHEN status = 'filled' THEN commission ELSE 0 END) as total_commission
                FROM order_history
                WHERE 1=1
            """
            params = {}
            
            if strategy_name:
                query += " AND strategy_name = %(strategy_name)s"
                params['strategy_name'] = strategy_name
            
            result = self.db.execute_single(query, params)
            
            if result:
                return {
                    'total_orders': result['total_orders'] or 0,
                    'filled_orders': result['filled_orders'] or 0,
                    'cancelled_orders': result['cancelled_orders'] or 0,
                    'pending_orders': result['pending_orders'] or 0,
                    'total_filled_quantity': float(result['total_filled_quantity'] or 0),
                    'avg_fill_price': float(result['avg_fill_price'] or 0),
                    'total_commission': float(result['total_commission'] or 0),
                    'fill_rate': (result['filled_orders'] / result['total_orders'] * 100) if result['total_orders'] > 0 else 0,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting order statistics: {str(e)}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the order manager.
        
        Returns:
            Dict with health check results
        """
        health_status = {
            'healthy': True,
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Database connectivity check
            health_status['checks']['database'] = {
                'status': 'pass' if self.db.check_connection() else 'fail',
                'message': 'Database connection is healthy'
            }
            
            # Kill switch check
            health_status['checks']['kill_switch'] = {
                'status': 'pass' if not self.is_kill_switch_active() else 'warn',
                'message': 'Kill switch is inactive' if not self.is_kill_switch_active() else f'Kill switch active: {self._kill_switch_reason}'
            }
            
            # Order data integrity check
            try:
                stats = self.get_order_statistics()
                health_status['checks']['order_data'] = {
                    'status': 'pass',
                    'message': f"Order data is healthy - {stats.get('total_orders', 0)} total orders"
                }
            except Exception as e:
                health_status['checks']['order_data'] = {
                    'status': 'warn',
                    'message': f"Order data check failed: {str(e)}"
                }
            
            # Determine overall health
            failed_checks = [name for name, check in health_status['checks'].items() if check['status'] == 'fail']
            if failed_checks:
                health_status['healthy'] = False
                health_status['failed_checks'] = failed_checks
            
        except Exception as e:
            logger.error(f"Error during order health check: {str(e)}")
            health_status['healthy'] = False
            health_status['error'] = str(e)
        
        return health_status
