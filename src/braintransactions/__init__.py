"""
BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, reliable, maintainable trading system following SRM principles.
"""

from .core.config import BrainConfig, get_config, init_config
from .database.connection import DatabaseManager
from .database.migrations import MigrationManager
from .markets.exchange_manager import ExchangeManager
from .core.monitoring import BackgroundMonitor
from .core.exceptions import *

__version__ = "2.0.0"
__author__ = "BrainTransactionsManager Team"

__all__ = [
    "BrainConfig",
    "get_config", 
    "init_config",
    "DatabaseManager",
    "MigrationManager",
    "ExchangeManager",
    "BackgroundMonitor"
]
