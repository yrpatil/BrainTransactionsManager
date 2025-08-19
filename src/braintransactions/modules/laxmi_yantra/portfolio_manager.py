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
