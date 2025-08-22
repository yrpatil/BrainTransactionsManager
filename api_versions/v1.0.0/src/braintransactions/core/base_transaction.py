"""
Base Transaction Manager for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Abstract base class for all transaction managers with common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from .kill_switch import KillSwitchMixin
from .config import BrainConfig
from .exceptions import TransactionExecutionError, InvalidConfigurationError

logger = logging.getLogger(__name__)

class BaseTransactionManager(KillSwitchMixin, ABC):
    """
    Abstract base class for all transaction managers.
    
    Features:
    • Kill switch support via mixin
    • Common transaction lifecycle management
    • Configuration management
    • Logging and monitoring
    • Error handling patterns
    • Audit trail maintenance
    """
    
    def __init__(self, config: Optional[BrainConfig] = None, module_name: str = "Unknown"):
        """
        Initialize base transaction manager.
        
        Args:
            config: Configuration instance (will create default if None)
            module_name: Name of the transaction module
        """
        super().__init__()  # Initialize KillSwitchMixin
        
        self.config = config or BrainConfig()
        self.module_name = module_name
        self.is_initialized = False
        self.transaction_count = 0
        self.last_transaction_time = None
        self.initialization_time = datetime.now()
        
        logger.info(f"🙏 Initializing {module_name} transaction manager")
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize module-specific components
        self._initialize_components()
        
        self.is_initialized = True
        logger.info(f"✅ {module_name} transaction manager initialized successfully")
    
    def _validate_configuration(self) -> None:
        """Validate required configuration."""
        try:
            # Check basic configuration
            if not self.config:
                raise InvalidConfigurationError("Configuration object is required")
            
            # Module-specific validation
            self._validate_module_configuration()
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise InvalidConfigurationError(f"Invalid configuration for {self.module_name}: {str(e)}")
    
    @abstractmethod
    def _validate_module_configuration(self) -> None:
        """Validate module-specific configuration. To be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _initialize_components(self) -> None:
        """Initialize module-specific components. To be implemented by subclasses."""
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for monitoring.
        
        Returns:
            Dict with system status information
        """
        base_status = {
            'module_name': self.module_name,
            'is_initialized': self.is_initialized,
            'initialization_time': self.initialization_time.isoformat(),
            'transaction_count': self.transaction_count,
            'last_transaction_time': self.last_transaction_time.isoformat() if self.last_transaction_time else None,
            'uptime_seconds': (datetime.now() - self.initialization_time).total_seconds(),
            'kill_switch_status': self.get_kill_switch_status(),
            'config_status': self.config.get_system_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add module-specific status
        try:
            module_status = self._get_module_status()
            base_status.update(module_status)
        except Exception as e:
            logger.error(f"Error getting module status: {str(e)}")
            base_status['module_status_error'] = str(e)
        
        return base_status
    
    @abstractmethod
    def _get_module_status(self) -> Dict[str, Any]:
        """Get module-specific status. To be implemented by subclasses."""
        pass
    
    def execute_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a transaction with full lifecycle management.
        
        Args:
            transaction_data: Transaction details
            
        Returns:
            Dict with transaction results
            
        Raises:
            KillSwitchActiveError: If kill switch is active
            TransactionExecutionError: If transaction fails
        """
        self.check_kill_switch_and_raise("transaction execution")
        
        transaction_id = f"{self.module_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        logger.info(f"🔄 Starting transaction {transaction_id}")
        
        try:
            # Pre-transaction validation
            self._validate_transaction(transaction_data)
            
            # Execute the actual transaction
            result = self._execute_transaction_impl(transaction_data, transaction_id)
            
            # Post-transaction processing
            self._post_transaction_processing(transaction_data, result, transaction_id)
            
            # Update metrics
            self.transaction_count += 1
            self.last_transaction_time = datetime.now()
            
            execution_time = (self.last_transaction_time - start_time).total_seconds()
            logger.info(f"✅ Transaction {transaction_id} completed successfully in {execution_time:.3f}s")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'execution_time_seconds': execution_time,
                'result': result,
                'timestamp': self.last_transaction_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Transaction {transaction_id} failed after {execution_time:.3f}s: {str(e)}")
            
            # Handle transaction failure
            self._handle_transaction_failure(transaction_data, str(e), transaction_id)
            
            raise TransactionExecutionError(
                f"Transaction {transaction_id} failed: {str(e)}",
                transaction_id=transaction_id,
                details={'execution_time_seconds': execution_time}
            )
    
    @abstractmethod
    def _validate_transaction(self, transaction_data: Dict[str, Any]) -> None:
        """Validate transaction data before execution. To be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _execute_transaction_impl(self, transaction_data: Dict[str, Any], transaction_id: str) -> Dict[str, Any]:
        """Execute the actual transaction logic. To be implemented by subclasses."""
        pass
    
    def _post_transaction_processing(self, transaction_data: Dict[str, Any], 
                                   result: Dict[str, Any], transaction_id: str) -> None:
        """
        Post-transaction processing (logging, cleanup, etc.).
        Can be overridden by subclasses for custom behavior.
        """
        # Default implementation - log the transaction
        logger.debug(f"Post-processing transaction {transaction_id}")
    
    def _handle_transaction_failure(self, transaction_data: Dict[str, Any], 
                                  error_message: str, transaction_id: str) -> None:
        """
        Handle transaction failure (cleanup, rollback, etc.).
        Can be overridden by subclasses for custom behavior.
        """
        # Default implementation - log the failure
        logger.error(f"Handling failure for transaction {transaction_id}: {error_message}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the transaction manager.
        
        Returns:
            Dict with health check results
        """
        health_status = {
            'healthy': True,
            'module_name': self.module_name,
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Basic health checks
            health_status['checks']['initialization'] = {
                'status': 'pass' if self.is_initialized else 'fail',
                'message': 'Manager is properly initialized'
            }
            
            health_status['checks']['kill_switch'] = {
                'status': 'pass' if not self.is_kill_switch_active() else 'warn',
                'message': 'Kill switch is inactive' if not self.is_kill_switch_active() else f'Kill switch active: {self._kill_switch_reason}'
            }
            
            health_status['checks']['configuration'] = {
                'status': 'pass' if self.config else 'fail',
                'message': 'Configuration is valid'
            }
            
            # Module-specific health checks
            module_checks = self._perform_module_health_checks()
            health_status['checks'].update(module_checks)
            
            # Determine overall health
            failed_checks = [name for name, check in health_status['checks'].items() if check['status'] == 'fail']
            if failed_checks:
                health_status['healthy'] = False
                health_status['failed_checks'] = failed_checks
            
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}")
            health_status['healthy'] = False
            health_status['error'] = str(e)
        
        return health_status
    
    @abstractmethod
    def _perform_module_health_checks(self) -> Dict[str, Dict[str, str]]:
        """Perform module-specific health checks. To be implemented by subclasses."""
        pass
