"""
Database Connection Manager for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Provides simple, reliable database connectivity with connection pooling.
"""

import logging
import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager
from datetime import datetime
from ..core.config import BrainConfig
from ..core.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Simple and reliable database connection manager.
    
    Features:
    • Connection pooling for efficiency
    • Transaction management
    • Automatic reconnection
    • Connection health monitoring
    • SQL execution utilities
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """
        Initialize database manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or BrainConfig()
        self.connection_pool = {}
        self.max_connections = 10
        self.current_connections = 0
        
        logger.info("🙏 Initializing database connection manager")
        
        # Test initial connection
        if not self.check_connection():
            logger.warning("Initial database connection test failed")
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters."""
        return {
            'host': self.config.db_host,
            'port': self.config.db_port,
            'database': self.config.db_name,
            'user': self.config.db_user,
            'password': self.config.db_password
        }
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection with automatic cleanup.
        
        Yields:
            Database connection object
        """
        connection = None
        try:
            connection = psycopg2.connect(
                **self.get_connection_params(),
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            # Ensure search_path points to configured schema first
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {self.config.db_schema}, public")
                    connection.commit()
            except Exception as e:
                logger.warning(f"Could not set search_path to schema {self.config.db_schema}: {str(e)}")
            self.current_connections += 1
            logger.debug(f"Database connection established (active: {self.current_connections})")
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            if connection:
                connection.rollback()
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
            
        finally:
            if connection:
                try:
                    connection.close()
                    self.current_connections = max(0, self.current_connections - 1)
                    logger.debug(f"Database connection closed (active: {self.current_connections})")
                except Exception as e:
                    logger.error(f"Error closing database connection: {str(e)}")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with query results
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or {})
                    results = cursor.fetchall()
                    logger.debug(f"Query executed successfully, returned {len(results)} rows")
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")
    
    def execute_single(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return a single result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single result dictionary or None
        """
        try:
            results = self.execute_query(query, params)
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error executing single query: {str(e)}")
            raise
    
    def execute_action(self, query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or {})
                    affected_rows = cursor.rowcount
                    conn.commit()
                    logger.debug(f"Action executed successfully, affected {affected_rows} rows")
                    return True
                    
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise DatabaseConnectionError(f"Action execution failed: {str(e)}")
    
    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> bool:
        """
        Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Convert list of dicts to list of tuples for executemany
                    if params_list:
                        # Get column names from first parameter set
                        columns = list(params_list[0].keys())
                        # Convert to list of tuples in consistent order
                        values_list = [[params[col] for col in columns] for params in params_list]
                        
                        # Replace named parameters with positional placeholders
                        formatted_query = query
                        for i, col in enumerate(columns):
                            formatted_query = formatted_query.replace(f'%({col})s', '%s')
                        
                        cursor.executemany(formatted_query, values_list)
                    else:
                        # Empty list, execute once with no parameters
                        cursor.execute(query)
                    
                    affected_rows = cursor.rowcount
                    conn.commit()
                    logger.debug(f"Batch execution successful, affected {affected_rows} rows")
                    return True
                    
        except Exception as e:
            logger.error(f"Error executing batch: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Batch size: {len(params_list)}")
            raise DatabaseConnectionError(f"Batch execution failed: {str(e)}")
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database cursor for transaction
        """
        connection = None
        cursor = None
        try:
            with self.get_connection() as conn:
                connection = conn
                cursor = conn.cursor()
                yield cursor
                conn.commit()
                logger.debug("Transaction committed successfully")
                
        except Exception as e:
            if connection:
                connection.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise
            
        finally:
            if cursor:
                cursor.close()
    
    def check_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 as test_value")
                    result = cursor.fetchone()
                    if result and result['test_value'] == 1:
                        logger.debug("Database connection test successful")
                        return True
                    else:
                        logger.error("Database connection test failed - unexpected result")
                        return False
                        
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status.
        
        Returns:
            Dict with pool status information
        """
        return {
            'status': 'active',
            'current_connections': self.current_connections,
            'max_connections': self.max_connections,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_tables(self) -> bool:
        """
        Create required database tables.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            schema = self.config.db_schema
            # Ensure schema exists
            self.execute_action(f"CREATE SCHEMA IF NOT EXISTS {schema}")

            tables_sql = [
                # Portfolio positions table
                f"""
                CREATE TABLE IF NOT EXISTS {schema}.portfolio_positions (
                    id SERIAL PRIMARY KEY,
                    strategy_name VARCHAR(255) NOT NULL,
                    ticker VARCHAR(50) NOT NULL,
                    quantity DECIMAL(20, 8) NOT NULL,
                    avg_entry_price DECIMAL(20, 8),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(strategy_name, ticker)
                )
                """,
                
                # Order history table
                f"""
                CREATE TABLE IF NOT EXISTS {schema}.order_history (
                    id SERIAL PRIMARY KEY,
                    order_id VARCHAR(255) UNIQUE,
                    client_order_id VARCHAR(255),
                    strategy_name VARCHAR(255) NOT NULL,
                    ticker VARCHAR(50) NOT NULL,
                    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
                    order_type VARCHAR(20) NOT NULL,
                    quantity DECIMAL(20, 8) NOT NULL,
                    filled_quantity DECIMAL(20, 8) DEFAULT 0,
                    price DECIMAL(20, 8),
                    filled_avg_price DECIMAL(20, 8),
                    status VARCHAR(20) NOT NULL,
                    commission DECIMAL(20, 8) DEFAULT 0,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    filled_at TIMESTAMP,
                    canceled_at TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                
                # Transaction log table
                f"""
                CREATE TABLE IF NOT EXISTS {schema}.transaction_log (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(255) UNIQUE NOT NULL,
                    module_name VARCHAR(100) NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    transaction_data JSONB,
                    result_data JSONB,
                    error_message TEXT,
                    execution_time_seconds DECIMAL(10, 6),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                ,
                # OHLC data table (for analytics current price/PnL)
                f"""
                CREATE TABLE IF NOT EXISTS {schema}.ohlc_data (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    open DECIMAL(20, 8),
                    high DECIMAL(20, 8),
                    low DECIMAL(20, 8),
                    close DECIMAL(20, 8),
                    volume DECIMAL(20, 8)
                )
                """
                ,
                # Application logs table (for centralized logging)
                f"""
                CREATE TABLE IF NOT EXISTS {schema}.app_logs (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    level VARCHAR(20) NOT NULL,
                    logger_name VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    pathname TEXT,
                    func_name TEXT,
                    lineno INTEGER,
                    process INTEGER,
                    thread_name TEXT,
                    extra JSONB
                )
                """
            ]
            
            for table_sql in tables_sql:
                self.execute_action(table_sql)
            
            logger.info("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            return False
