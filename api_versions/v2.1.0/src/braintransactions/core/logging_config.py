"""
Sophisticated Logging Configuration for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Provides clean, relevant logging for production and detailed logging for debug mode.
Follows SRM principles: Simple, Reliable, Maintainable.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json


class BrainLogger:
    """
    Sophisticated logging system for BrainTransactionsManager.
    
    Features:
    • Clean, relevant logs for production
    • Detailed logs for debug mode
    • Structured logging with context
    • Performance monitoring
    • Error tracking and reporting
    """
    
    def __init__(self, name: str, log_level: str = "INFO", debug_mode: bool = False):
        self.name = name
        self.log_level = log_level.upper()
        self.debug_mode = debug_mode
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with appropriate configuration."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.log_level))
        
        # Prevent propagation to root logger to avoid duplicates
        logger.propagate = False
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        if self.debug_mode:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for production
        if not self.debug_mode:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"braintransactions_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def startup(self, message: str, **kwargs):
        """Log startup information."""
        if self.debug_mode:
            self.logger.info(f"🚀 {message}", extra=kwargs)
        else:
            self.logger.info(f"🚀 {message}")
    
    def success(self, message: str, **kwargs):
        """Log success information."""
        if self.debug_mode:
            self.logger.info(f"✅ {message}", extra=kwargs)
        else:
            self.logger.info(f"✅ {message}")
    
    def error(self, message: str, **kwargs):
        """Log error information."""
        if self.debug_mode:
            self.logger.error(f"❌ {message}", extra=kwargs)
        else:
            self.logger.error(f"❌ {message}")
    
    def warning(self, message: str, **kwargs):
        """Log warning information."""
        if self.debug_mode:
            self.logger.warning(f"⚠️ {message}", extra=kwargs)
        else:
            self.logger.warning(f"⚠️ {message}")
    
    def info(self, message: str, **kwargs):
        """Log general information."""
        if self.debug_mode:
            self.logger.info(f"ℹ️ {message}", extra=kwargs)
        else:
            self.logger.info(f"ℹ️ {message}")
    
    def debug(self, message: str, **kwargs):
        """Log debug information (only in debug mode)."""
        if self.debug_mode:
            self.logger.debug(f"🔍 {message}", extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical information."""
        if self.debug_mode:
            self.logger.critical(f"🚨 {message}", extra=kwargs)
        else:
            self.logger.critical(f"🚨 {message}")
    
    def blessing(self, message: str):
        """Log blessing messages."""
        self.logger.info(f"🙏 {message}")
    
    def trading(self, action: str, symbol: str, quantity: float, **kwargs):
        """Log trading actions."""
        if self.debug_mode:
            self.logger.info(f"💰 {action}: {symbol} x {quantity}", extra=kwargs)
        else:
            self.logger.info(f"💰 {action}: {symbol} x {quantity}")
    
    def performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics."""
        if self.debug_mode:
            self.logger.info(f"⚡ {operation}: {duration_ms:.2f}ms", extra=kwargs)
        else:
            if duration_ms > 1000:  # Only log slow operations in production
                self.logger.warning(f"⚡ {operation}: {duration_ms:.2f}ms")
    
    def health(self, component: str, status: str, **kwargs):
        """Log health check information."""
        if self.debug_mode:
            self.logger.info(f"🏥 {component}: {status}", extra=kwargs)
        else:
            if status.lower() != "healthy":
                self.logger.warning(f"🏥 {component}: {status}")
    
    def request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Log HTTP request information."""
        if self.debug_mode:
            self.logger.info(f"🌐 {method} {path} → {status_code} ({duration_ms:.1f}ms)", extra=kwargs)
        else:
            # Only log non-200 responses and slow requests in production
            if status_code != 200 or duration_ms > 1000:
                self.logger.info(f"🌐 {method} {path} → {status_code} ({duration_ms:.1f}ms)")
    
    def transaction(self, action: str, symbol: str, quantity: float, order_type: str = "market", **kwargs):
        """Log trading transaction details."""
        if self.debug_mode:
            self.logger.info(f"💼 {action}: {symbol} x {quantity} ({order_type})", extra=kwargs)
        else:
            self.logger.info(f"💼 {action}: {symbol} x {quantity} ({order_type})")
    
    def order_status(self, order_id: str, symbol: str, status: str, **kwargs):
        """Log order status changes."""
        if self.debug_mode:
            self.logger.info(f"📋 Order {order_id[:8]}... ({symbol}) → {status}", extra=kwargs)
        else:
            if status in ['filled', 'cancelled', 'rejected']:
                self.logger.info(f"📋 Order {order_id[:8]}... ({symbol}) → {status}")
    
    def portfolio_update(self, action: str, symbol: str, quantity: float, value: float, **kwargs):
        """Log portfolio updates."""
        if self.debug_mode:
            self.logger.info(f"📊 {action}: {symbol} x {quantity} = ${value:.2f}", extra=kwargs)
        else:
            self.logger.info(f"📊 {action}: {symbol} x {quantity} = ${value:.2f}")
    
    def system_event(self, event: str, details: str = "", **kwargs):
        """Log system events."""
        if self.debug_mode:
            self.logger.info(f"⚙️ {event}: {details}", extra=kwargs)
        else:
            self.logger.info(f"⚙️ {event}: {details}")
    
    def error_with_context(self, error: str, context: str, **kwargs):
        """Log errors with context."""
        if self.debug_mode:
            self.logger.error(f"❌ {error} | Context: {context}", extra=kwargs)
        else:
            self.logger.error(f"❌ {error} | Context: {context}")


class SystemLogger:
    """
    System-wide logger for BrainTransactionsManager.
    Provides consistent logging across all components.
    """
    
    _instance = None
    _loggers: Dict[str, BrainLogger] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
            self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def get_logger(self, name: str) -> BrainLogger:
        """Get or create a logger for the given component."""
        if name not in self._loggers:
            self._loggers[name] = BrainLogger(
                name=name,
                log_level=self.log_level,
                debug_mode=self.debug_mode
            )
        return self._loggers[name]
    
    def startup_sequence(self):
        """Log the startup sequence."""
        logger = self.get_logger("system")
        logger.blessing("Starting BrainTransactionsManager v2.0.0...")
        logger.blessing("May Goddess Laxmi bless this session with infinite abundance!")
        
        if self.debug_mode:
            logger.info("Debug mode enabled - detailed logging active")
    
    def shutdown_sequence(self):
        """Log the shutdown sequence."""
        logger = self.get_logger("system")
        logger.info("🔄 Shutting down BrainTransactionsManager v2.0.0...")
        logger.success("System shutdown complete")


# Global system logger instance
system_logger = SystemLogger()


def get_logger(name: str) -> BrainLogger:
    """Get a logger for the specified component."""
    return system_logger.get_logger(name)


def setup_logging(debug_mode: bool = False, log_level: str = "INFO"):
    """Setup the logging system."""
    system_logger.debug_mode = debug_mode
    system_logger.log_level = log_level
    
    # Configure root logger
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    return system_logger
