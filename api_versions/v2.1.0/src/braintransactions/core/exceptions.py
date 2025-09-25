"""
Exception classes for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, clear exception hierarchy for error handling.
"""


class BrainTransactionError(Exception):
    """Base exception for all BrainTransaction errors."""
    pass


class DatabaseConnectionError(BrainTransactionError):
    """Database connection and query errors."""
    pass


class ConfigurationError(BrainTransactionError):
    """Configuration validation errors."""
    pass


class TradingError(BrainTransactionError):
    """Trading operation errors."""
    pass


class MarketAdapterError(BrainTransactionError):
    """Market adapter errors."""
    pass


class KillSwitchError(BrainTransactionError):
    """Kill switch activation errors."""
    pass


class ValidationError(BrainTransactionError):
    """Data validation errors."""
    pass


class MigrationError(BrainTransactionError):
    """Database migration errors."""
    pass
