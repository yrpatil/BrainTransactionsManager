"""
Exception classes for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Custom exceptions for better error handling and debugging in the transaction system.
"""

from typing import Optional, Dict, Any

class BrainTransactionError(Exception):
    """Base exception for all BrainTransactionsManager errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class TransactionExecutionError(BrainTransactionError):
    """Raised when a transaction fails to execute properly."""
    
    def __init__(self, message: str, transaction_id: Optional[str] = None, 
                 ticker: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.transaction_id = transaction_id
        self.ticker = ticker
        super().__init__(message, "TRANSACTION_EXECUTION_ERROR", details)

class KillSwitchActiveError(BrainTransactionError):
    """Raised when attempting operations while kill switch is active."""
    
    def __init__(self, message: str = "Operation blocked - kill switch is active", 
                 operation: Optional[str] = None):
        self.operation = operation
        details = {"operation": operation} if operation else {}
        super().__init__(message, "KILL_SWITCH_ACTIVE", details)

class InvalidConfigurationError(BrainTransactionError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.config_key = config_key
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, "INVALID_CONFIGURATION", details)

class InsufficientFundsError(BrainTransactionError):
    """Raised when there are insufficient funds for a transaction."""
    
    def __init__(self, message: str, required_amount: Optional[float] = None, 
                 available_amount: Optional[float] = None):
        self.required_amount = required_amount
        self.available_amount = available_amount
        details = {
            "required_amount": required_amount,
            "available_amount": available_amount
        }
        super().__init__(message, "INSUFFICIENT_FUNDS", details)

class OrderValidationError(BrainTransactionError):
    """Raised when order validation fails."""
    
    def __init__(self, message: str, order_data: Optional[Dict[str, Any]] = None):
        self.order_data = order_data
        super().__init__(message, "ORDER_VALIDATION_ERROR", {"order_data": order_data})

class DatabaseConnectionError(BrainTransactionError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str, connection_details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_CONNECTION_ERROR", connection_details)

class PositionNotFoundError(BrainTransactionError):
    """Raised when attempting to operate on a non-existent position."""
    
    def __init__(self, message: str, strategy_name: Optional[str] = None, 
                 ticker: Optional[str] = None):
        self.strategy_name = strategy_name
        self.ticker = ticker
        details = {"strategy_name": strategy_name, "ticker": ticker}
        super().__init__(message, "POSITION_NOT_FOUND", details)

class APIConnectionError(BrainTransactionError):
    """Raised when external API connection fails."""
    
    def __init__(self, message: str, api_name: Optional[str] = None, 
                 status_code: Optional[int] = None):
        self.api_name = api_name
        self.status_code = status_code
        details = {"api_name": api_name, "status_code": status_code}
        super().__init__(message, "API_CONNECTION_ERROR", details)

class RiskManagementError(BrainTransactionError):
    """Raised when risk management rules are violated."""
    
    def __init__(self, message: str, risk_type: Optional[str] = None, 
                 violation_details: Optional[Dict[str, Any]] = None):
        self.risk_type = risk_type
        self.violation_details = violation_details or {}
        details = {"risk_type": risk_type, **self.violation_details}
        super().__init__(message, "RISK_MANAGEMENT_ERROR", details)
