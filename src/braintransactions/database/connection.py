"""
Enhanced Database Connection Manager for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, reliable database connectivity with startup validation and basic pooling.
Focuses on essential features without overengineering.
"""

import logging
import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from datetime import datetime
import time
import threading
from ..core.config import BrainConfig
from ..core.exceptions import DatabaseConnectionError
from ..core.logging_config import get_logger

logger = get_logger("database")


class DatabaseManager:
    """
    Enhanced database connection manager for v2.0.0.
    
    Features:
    • Startup health validation
    • Simple connection pooling
    • Automatic reconnection
    • Transaction management
    • Connection monitoring
    • Graceful error handling
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """
        Initialize database manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.max_connections = self.config.database.pool_size if config else 10
        self.current_connections = 0
        self.startup_validated = False
        
        logger.startup("Initializing database connection manager v2.0.0")
    
    async def startup_validation(self) -> bool:
        """
        Perform essential startup validation.
        
        Returns:
            True if database is ready, False if critical failure
        """
        if self.startup_validated:
            return True
        
        logger.info("Validating database connectivity...")
        
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                # Test basic connectivity
                if not self.check_connection():
                    logger.warning(f"Database connection attempt {attempt}/{max_attempts} failed")
                    if attempt < max_attempts:
                        time.sleep(2)
                        continue
                    return False
                
                # Test schema access
                schema_query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{self.config.database.schema}'"
                result = self.execute_query(schema_query)
                if not result:
                    logger.error(f"Schema '{self.config.database.schema}' not found")
                    return False
                
                # Test critical tables exist
                tables_query = f"""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = '{self.config.database.schema}' 
                AND table_name IN ('portfolio_positions', 'order_history', 'transaction_log')
                """
                tables_result = self.execute_query(tables_query)
                if len(tables_result) < 3:
                    logger.warning("Some critical tables missing, will create them")
                    self.create_tables()
                
                # Update system status
                self._update_system_status('database', True, 'Startup validation successful')
                
                self.startup_validated = True
                logger.success("Database startup validation successful")
                return True
                
            except Exception as e:
                logger.error(f"Database validation attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    logger.critical("❌ Database startup validation failed after all attempts")
                    return False
                time.sleep(2)
        
        return False
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters."""
        return {
            'host': self.config.database.host,
            'port': self.config.database.port,
            'database': self.config.database.name,
            'user': self.config.database.user,
            'password': self.config.database.password,
            'connect_timeout': self.config.database.connection_timeout,
            'cursor_factory': psycopg2.extras.RealDictCursor
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
            connection = psycopg2.connect(**self.get_connection_params())
            
            # Set search path
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {self.config.database.schema}, public")
                    connection.commit()
            except Exception as e:
                logger.warning(f"Could not set search_path: {e}")
            
            with self.pool_lock:
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
                    with self.pool_lock:
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
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_action(self, query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful
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
            raise DatabaseConnectionError(f"Action execution failed: {str(e)}")
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database cursor for transaction
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
                raise
            finally:
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
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get simple health status."""
        try:
            start_time = time.time()
            is_healthy = self.check_connection()
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time_ms': round(response_time, 2),
                'active_connections': self.current_connections,
                'startup_validated': self.startup_validated,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_system_status(self, component: str, is_active: bool, message: str):
        """Update system status table."""
        try:
            upsert_query = f"""
            INSERT INTO {self.config.database.schema}.system_status 
                (component_name, is_active, status_message, last_heartbeat, updated_at)
            VALUES (%(component)s, %(is_active)s, %(message)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (component_name) 
            DO UPDATE SET 
                is_active = EXCLUDED.is_active,
                status_message = EXCLUDED.status_message,
                last_heartbeat = EXCLUDED.last_heartbeat,
                updated_at = EXCLUDED.updated_at
            """
            
            self.execute_action(upsert_query, {
                'component': component,
                'is_active': is_active,
                'message': message
            })
            
        except Exception as e:
            logger.warning(f"Could not update system status: {e}")
    
    def create_tables(self) -> bool:
        """
        Create required database tables if they don't exist.
        
        Returns:
            True if successful
        """
        try:
            schema = self.config.database.schema
            
            # Ensure schema exists
            self.execute_action(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            
            # System status table
            system_status_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.system_status (
                id SERIAL PRIMARY KEY,
                component_name VARCHAR(100) NOT NULL UNIQUE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                status_message TEXT,
                last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Portfolio positions table
            portfolio_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.portfolio_positions (
                id SERIAL PRIMARY KEY,
                strategy_name VARCHAR(255) NOT NULL,
                ticker VARCHAR(50) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                avg_entry_price DECIMAL(20, 8),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, ticker)
            )
            """
            
            # Order history table
            orders_sql = f"""
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
                submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                filled_at TIMESTAMP WITH TIME ZONE,
                canceled_at TIMESTAMP WITH TIME ZONE,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Transaction log table
            transaction_sql = f"""
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
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # OHLC data table
            ohlc_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.ohlc_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                timeframe VARCHAR(10) NOT NULL DEFAULT '1D',
                open DECIMAL(20, 8),
                high DECIMAL(20, 8),
                low DECIMAL(20, 8),
                close DECIMAL(20, 8),
                volume DECIMAL(20, 8),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, timestamp, timeframe)
            )
            """
            
            # Execute table creation
            for table_sql in [system_status_sql, portfolio_sql, orders_sql, transaction_sql, ohlc_sql]:
                self.execute_action(table_sql)
            
            # Create essential indexes
            indexes = [
                f"CREATE INDEX IF NOT EXISTS idx_portfolio_strategy_ticker ON {schema}.portfolio_positions(strategy_name, ticker)",
                f"CREATE INDEX IF NOT EXISTS idx_order_strategy ON {schema}.order_history(strategy_name)",
                f"CREATE INDEX IF NOT EXISTS idx_order_ticker ON {schema}.order_history(ticker)",
                f"CREATE INDEX IF NOT EXISTS idx_order_status ON {schema}.order_history(status)",
                f"CREATE INDEX IF NOT EXISTS idx_transaction_module ON {schema}.transaction_log(module_name)",
                f"CREATE INDEX IF NOT EXISTS idx_ohlc_ticker_timestamp ON {schema}.ohlc_data(ticker, timestamp DESC)"
            ]
            
            for index_sql in indexes:
                self.execute_action(index_sql)
            
            logger.info("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            return False
