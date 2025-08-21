"""
Portfolio Manager for Laxmi-yantra Trading Module
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, reliable, and maintainable portfolio position tracking.
Built with kill switch support for graceful system shutdown.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime
from ...database import DatabaseManager
from ...core.kill_switch import KillSwitchMixin
from ...core.config import BrainConfig

logger = logging.getLogger(__name__)

class PortfolioManager(KillSwitchMixin):
    """
    Simple and reliable portfolio position management for Laxmi-yantra.
    
    Key Features:
    • Track positions per strategy and ticker
    • Automatic position cleanup when quantity = 0
    • Kill switch support for emergency shutdown
    • Strategy isolation for concurrent trading
    • Simple, maintainable code structure
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """Initialize the Portfolio Manager."""
        super().__init__()  # Initialize KillSwitchMixin
        
        self.config = config or BrainConfig()
        self.db = DatabaseManager(self.config)
        
        logger.info("🙏 Laxmi-yantra Portfolio Manager initialized")
        
        # Ensure database tables exist
        self.db.create_tables()
        
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status for monitoring.
        
        Returns:
            Dict with system status information
        """
        try:
            db_status = self.db.check_connection()
            
            return {
                'kill_switch_active': self.is_kill_switch_active(),
                'database_connected': db_status,
                'timestamp': datetime.now().isoformat(),
                'system_ready': not self.is_kill_switch_active() and db_status
            }
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'kill_switch_active': self.is_kill_switch_active(),
                'database_connected': False,
                'timestamp': datetime.now().isoformat(),
                'system_ready': False,
                'error': str(e)
            }
    
    def get_position(self, strategy_name: str, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get current position for a strategy and ticker.
        
        Args:
            strategy_name: Name of the strategy
            ticker: Trading symbol
            
        Returns:
            Dict with position data or None if not found
        """
        try:
            query = """
                SELECT strategy_name, ticker, quantity, avg_entry_price, 
                       last_updated, created_at
                FROM portfolio_positions
                WHERE strategy_name = %(strategy_name)s AND ticker = %(ticker)s
            """
            
            result = self.db.execute_single(query, {
                'strategy_name': strategy_name,
                'ticker': ticker
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting position: {str(e)}")
            return None
    
    def update_position(self, strategy_name: str, ticker: str, quantity: float, 
                       avg_price: Optional[float] = None) -> bool:
        """
        Update portfolio position for a strategy and ticker.
        
        Args:
            strategy_name: Name of the strategy
            ticker: Trading symbol
            quantity: New quantity (0 to close position)
            avg_price: Average entry price (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.check_kill_switch_and_raise("portfolio position update")
        
        try:
            if quantity == 0:
                # Remove position if quantity is 0
                query = """
                    DELETE FROM portfolio_positions
                    WHERE strategy_name = %(strategy_name)s AND ticker = %(ticker)s
                """
                self.db.execute_action(query, {
                    'strategy_name': strategy_name,
                    'ticker': ticker
                })
                logger.info(f"Position closed: {strategy_name} {ticker}")
            else:
                # Upsert position
                query = """
                    INSERT INTO portfolio_positions 
                    (strategy_name, ticker, quantity, avg_entry_price, last_updated)
                    VALUES (%(strategy_name)s, %(ticker)s, %(quantity)s, %(avg_price)s, CURRENT_TIMESTAMP)
                    ON CONFLICT (strategy_name, ticker) 
                    DO UPDATE SET 
                        quantity = EXCLUDED.quantity,
                        avg_entry_price = EXCLUDED.avg_entry_price,
                        last_updated = CURRENT_TIMESTAMP
                """
                self.db.execute_action(query, {
                    'strategy_name': strategy_name,
                    'ticker': ticker,
                    'quantity': quantity,
                    'avg_price': avg_price
                })
                logger.info(f"Position updated: {strategy_name} {ticker} {quantity}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
            return False
    
    def get_all_positions(self, strategy_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get all current positions with optional strategy filter.
        
        Args:
            strategy_name: Filter by strategy (optional)
            
        Returns:
            DataFrame with all positions
        """
        try:
            query = """
                SELECT strategy_name, ticker, quantity, avg_entry_price, 
                       last_updated, created_at
                FROM portfolio_positions
                WHERE 1=1
            """
            params = {}
            
            if strategy_name:
                query += " AND strategy_name = %(strategy_name)s"
                params['strategy_name'] = strategy_name
            
            query += " ORDER BY strategy_name, ticker"
            
            results = self.db.execute_query(query, params)
            
            if results:
                df = pd.DataFrame(results)
                df['last_updated'] = pd.to_datetime(df['last_updated'])
                df['created_at'] = pd.to_datetime(df['created_at'])
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting all positions: {str(e)}")
            return pd.DataFrame()
    
    def get_portfolio_summary(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio summary with current positions.
        
        Args:
            strategy_name: Filter by strategy (optional)
            
        Returns:
            Dictionary with portfolio summary
        """
        try:
            query = """
                SELECT 
                    strategy_name,
                    COUNT(*) as total_positions,
                    SUM(quantity) as total_quantity,
                    AVG(avg_entry_price) as avg_price,
                    MAX(last_updated) as last_updated
                FROM portfolio_positions
                WHERE 1=1
            """
            params = {}
            
            if strategy_name:
                query += " AND strategy_name = %(strategy_name)s"
                params['strategy_name'] = strategy_name
            
            query += " GROUP BY strategy_name"
            
            results = self.db.execute_query(query, params)
            
            if results:
                return results[0]  # Return first result
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {}

    def get_strategy_summary(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get a concise strategy summary combining positions and orders.
        Returns counts and timestamps useful for monitoring.
        """
        try:
            # Positions summary
            pos_query = """
                SELECT 
                    COUNT(*)::int AS total_positions,
                    COALESCE(SUM(quantity), 0) AS total_quantity,
                    COALESCE(AVG(avg_entry_price), 0) AS avg_entry_price,
                    MAX(last_updated) AS last_position_update
                FROM portfolio_positions
                WHERE strategy_name = %(strategy)s
            """
            pos_summary = self.db.execute_single(pos_query, {"strategy": strategy_name}) or {}

            # Order counts
            order_counts_query = """
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'pending')::int AS pending_orders,
                    COUNT(*) FILTER (WHERE status = 'filled')::int AS filled_orders,
                    COUNT(*) FILTER (WHERE status = 'cancelled')::int AS cancelled_orders,
                    COUNT(*)::int AS total_orders,
                    MAX(submitted_at) AS last_order_time
                FROM order_history
                WHERE strategy_name = %(strategy)s
            """
            order_counts = self.db.execute_single(order_counts_query, {"strategy": strategy_name}) or {}

            # Recent fills in last 24h
            fills_24h_query = """
                SELECT COUNT(*)::int AS fills_24h
                FROM order_history
                WHERE strategy_name = %(strategy)s
                  AND status = 'filled'
                  AND submitted_at >= NOW() - INTERVAL '24 hours'
            """
            fills_24h = self.db.execute_single(fills_24h_query, {"strategy": strategy_name}) or {"fills_24h": 0}

            summary: Dict[str, Any] = {
                "strategy_name": strategy_name,
                "total_positions": pos_summary.get("total_positions", 0) or 0,
                "total_quantity": float(pos_summary.get("total_quantity", 0) or 0),
                "avg_entry_price": float(pos_summary.get("avg_entry_price", 0) or 0),
                "last_position_update": pos_summary.get("last_position_update"),
                "pending_orders": order_counts.get("pending_orders", 0) or 0,
                "filled_orders": order_counts.get("filled_orders", 0) or 0,
                "cancelled_orders": order_counts.get("cancelled_orders", 0) or 0,
                "total_orders": order_counts.get("total_orders", 0) or 0,
                "last_order_time": order_counts.get("last_order_time"),
                "fills_24h": fills_24h.get("fills_24h", 0) or 0,
                "timestamp": datetime.now().isoformat(),
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting strategy summary: {str(e)}")
            return {"strategy_name": strategy_name, "error": str(e)}
    
    def close_all_positions(self, strategy_name: str) -> bool:
        """
        Close all positions for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.check_kill_switch_and_raise("close all positions")
        
        try:
            query = """
                DELETE FROM portfolio_positions
                WHERE strategy_name = %(strategy_name)s
            """
            self.db.execute_action(query, {'strategy_name': strategy_name})
            logger.warning(f"All positions closed for strategy: {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")
            return False
    
    def validate_portfolio_consistency(self) -> Dict[str, Any]:
        """
        Validate portfolio data consistency.
        
        Returns:
            Dict with validation results
        """
        try:
            # Check for negative quantities
            negative_query = """
                SELECT COUNT(*) as negative_count
                FROM portfolio_positions
                WHERE quantity < 0
            """
            negative_result = self.db.execute_single(negative_query)
            negative_count = negative_result['negative_count'] if negative_result else 0
            
            # Check for zero quantities (should be cleaned up)
            zero_query = """
                SELECT COUNT(*) as zero_count
                FROM portfolio_positions
                WHERE quantity = 0
            """
            zero_result = self.db.execute_single(zero_query)
            zero_count = zero_result['zero_count'] if zero_result else 0
            
            # Check total positions
            total_query = """
                SELECT COUNT(*) as total_count
                FROM portfolio_positions
            """
            total_result = self.db.execute_single(total_query)
            total_count = total_result['total_count'] if total_result else 0
            
            return {
                'is_consistent': negative_count == 0 and zero_count == 0,
                'total_positions': total_count,
                'negative_quantities': negative_count,
                'zero_quantities': zero_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating portfolio consistency: {str(e)}")
            return {
                'is_consistent': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def reconcile_positions_from_alpaca(self, alpaca_positions: Optional[list], strategy_name: str = 'default') -> bool:
        """Reconcile DB positions with Alpaca positions (overwrite DB snapshot).
        Minimal approach: upsert each Alpaca position; remove any DB positions not present in Alpaca.
        """
        try:
            if alpaca_positions is None:
                return True
            # Build set for present tickers
            present = set()
            for p in alpaca_positions:
                symbol = getattr(p, 'symbol', None) or getattr(p, 'asset_id', None)
                qty = float(getattr(p, 'qty', 0))
                avg = float(getattr(p, 'avg_entry_price', 0) or 0)
                if not symbol:
                    continue
                present.add(symbol)
                if qty <= 0:
                    self.update_position(strategy_name, symbol, 0)
                else:
                    self.update_position(strategy_name, symbol, qty, avg)
            # Remove positions missing from Alpaca for default strategy
            all_df = self.get_all_positions(strategy_name)
            if not all_df.empty:
                for _, row in all_df.iterrows():
                    if row['ticker'] not in present:
                        self.update_position(strategy_name, row['ticker'], 0)
            return True
        except Exception as e:
            logger.error(f"Error during position reconciliation: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the portfolio manager.
        
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
            
            # Data consistency check
            consistency = self.validate_portfolio_consistency()
            health_status['checks']['data_consistency'] = {
                'status': 'pass' if consistency['is_consistent'] else 'warn',
                'message': 'Portfolio data is consistent' if consistency['is_consistent'] else 'Portfolio data inconsistencies detected'
            }
            
            # Determine overall health
            failed_checks = [name for name, check in health_status['checks'].items() if check['status'] == 'fail']
            if failed_checks:
                health_status['healthy'] = False
                health_status['failed_checks'] = failed_checks
            
        except Exception as e:
            logger.error(f"Error during portfolio health check: {str(e)}")
            health_status['healthy'] = False
            health_status['error'] = str(e)
        
        return health_status
