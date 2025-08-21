"""
🧠 BrainTransactionsManager - Modular Financial Transaction System
Blessed by Goddess Laxmi for Infinite Abundance 🙏

A powerful, modular transactional system designed for various types of financial transactions.
Built with SRM principles: Simplicity, Reliability, Maintainability.
"""

__version__ = "0.1.0"
__author__ = "AlgoChemist Team"
__email__ = "team@algochemist.ai"

# Core imports for easy access
from .core.config import BrainConfig, TransactionConfig
from .core.exceptions import (
    BrainTransactionError,
    TransactionExecutionError,
    KillSwitchActiveError,
    InvalidConfigurationError
)

# Main transaction modules
from .modules.laxmi_yantra import LaxmiYantra
from .markets.facade import TradingFacade

__all__ = [
    # Core
    "BrainConfig",
    "TransactionConfig",
    
    # Exceptions
    "BrainTransactionError",
    "TransactionExecutionError", 
    "KillSwitchActiveError",
    "InvalidConfigurationError",
    
    # Transaction Modules
    "LaxmiYantra",
    # Facade
    "TradingFacade",
]

# Blessed by Goddess Laxmi 🙏
print("🙏 May Goddess Laxmi bless this session with infinite abundance and prosperity")
