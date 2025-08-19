"""
Configuration management for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

This module provides centralized configuration management following SRM principles:
- Simplicity: Clear, consistent configuration structure
- Reliability: Environment validation and secure secret management
- Maintainability: Single source of truth for all settings
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class TransactionConfig:
    """Configuration for transaction system behavior."""
    
    # Kill switch settings
    kill_switch_timeout: int = 30
    
    # Retry settings
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    
    # Position management
    default_position_size: float = 100.0
    max_position_size_percent: float = 10.0
    
    # Risk management
    max_daily_loss_percent: float = 5.0
    max_single_asset_allocation: float = 25.0
    
    # Paper trading
    paper_trading: bool = True
    paper_trading_capital: float = 100000.0

class BrainConfig:
    """
    Centralized configuration management for BrainTransactionsManager.
    
    Features:
    • Environment variable validation
    • Secure credential management
    • Transaction system configuration
    • Database connection settings
    • Logging configuration
    """
    
    # Required environment variables
    REQUIRED_ENV_VARS = [
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY'
    ]
    
    # Optional environment variables with defaults
    OPTIONAL_ENV_VARS = {
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
        'ALPACA_DATA_URL': 'https://data.alpaca.markets/v2',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'braintransactions',
        'DB_USER': 'brain_user',
        'DB_PASSWORD': 'brain_password',
        'LOG_LEVEL': 'INFO',
        'LOG_FILE_PATH': 'logs/braintransactions.log',
        'PAPER_TRADING': 'true',
        'PAPER_TRADING_CAPITAL': '100000.0',
        'DEFAULT_POSITION_SIZE': '100.0',
        'KILL_SWITCH_TIMEOUT': '30',
        'MAX_RETRY_ATTEMPTS': '3',
        'RETRY_DELAY_SECONDS': '1.0',
        'MAX_POSITION_SIZE_PERCENT': '10.0',
        'MAX_DAILY_LOSS_PERCENT': '5.0',
        'MAX_SINGLE_ASSET_ALLOCATION': '25.0'
    }
    
    def __init__(self):
        """Initialize configuration with validation."""
        self._validate_environment()
        self._load_configuration()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("🙏 BrainTransactionsManager configuration loaded successfully")
        logger.info(f"Paper trading mode: {self.paper_trading}")
        logger.info(f"Alpaca endpoint: {self.alpaca_base_url}")
    
    def _validate_environment(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = []
        for var in self.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {missing_vars}. "
                "Please check your .env file or set these environment variables."
            )
    
    def _load_configuration(self) -> None:
        """Load all configuration values from environment."""
        
        # Alpaca API configuration
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', self.OPTIONAL_ENV_VARS['ALPACA_BASE_URL'])
        self.alpaca_data_url = os.getenv('ALPACA_DATA_URL', self.OPTIONAL_ENV_VARS['ALPACA_DATA_URL'])
        
        # Database configuration
        self.db_host = os.getenv('DB_HOST', self.OPTIONAL_ENV_VARS['DB_HOST'])
        self.db_port = int(os.getenv('DB_PORT', self.OPTIONAL_ENV_VARS['DB_PORT']))
        self.db_name = os.getenv('DB_NAME', self.OPTIONAL_ENV_VARS['DB_NAME'])
        self.db_user = os.getenv('DB_USER', self.OPTIONAL_ENV_VARS['DB_USER'])
        self.db_password = os.getenv('DB_PASSWORD', self.OPTIONAL_ENV_VARS['DB_PASSWORD'])
        self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', self.OPTIONAL_ENV_VARS['LOG_LEVEL'])
        self.log_file_path = os.getenv('LOG_FILE_PATH', self.OPTIONAL_ENV_VARS['LOG_FILE_PATH'])
        
        # Transaction configuration
        self.transaction_config = TransactionConfig(
            kill_switch_timeout=int(os.getenv('KILL_SWITCH_TIMEOUT', self.OPTIONAL_ENV_VARS['KILL_SWITCH_TIMEOUT'])),
            max_retry_attempts=int(os.getenv('MAX_RETRY_ATTEMPTS', self.OPTIONAL_ENV_VARS['MAX_RETRY_ATTEMPTS'])),
            retry_delay_seconds=float(os.getenv('RETRY_DELAY_SECONDS', self.OPTIONAL_ENV_VARS['RETRY_DELAY_SECONDS'])),
            default_position_size=float(os.getenv('DEFAULT_POSITION_SIZE', self.OPTIONAL_ENV_VARS['DEFAULT_POSITION_SIZE'])),
            max_position_size_percent=float(os.getenv('MAX_POSITION_SIZE_PERCENT', self.OPTIONAL_ENV_VARS['MAX_POSITION_SIZE_PERCENT'])),
            max_daily_loss_percent=float(os.getenv('MAX_DAILY_LOSS_PERCENT', self.OPTIONAL_ENV_VARS['MAX_DAILY_LOSS_PERCENT'])),
            max_single_asset_allocation=float(os.getenv('MAX_SINGLE_ASSET_ALLOCATION', self.OPTIONAL_ENV_VARS['MAX_SINGLE_ASSET_ALLOCATION'])),
            paper_trading=os.getenv('PAPER_TRADING', self.OPTIONAL_ENV_VARS['PAPER_TRADING']).lower() == 'true',
            paper_trading_capital=float(os.getenv('PAPER_TRADING_CAPITAL', self.OPTIONAL_ENV_VARS['PAPER_TRADING_CAPITAL']))
        )
        
        # Convenience properties
        self.paper_trading = self.transaction_config.paper_trading
        self.paper_trading_capital = self.transaction_config.paper_trading_capital
        
        # Optional configurations
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_allowed_users = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if os.getenv('TELEGRAM_ALLOWED_USERS') else []
    
    def _setup_logging(self) -> None:
        """Setup structured logging configuration."""
        
        # Convert log level string to logging constant
        numeric_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        # Create log directory if it doesn't exist
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        
        # Setup file handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Clear existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Suppress noisy loggers
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('psycopg2').setLevel(logging.WARNING)
        logging.getLogger('alpaca_trade_api').setLevel(logging.WARNING)
    
    def get_alpaca_credentials(self) -> Dict[str, str]:
        """Get Alpaca API credentials."""
        return {
            'api_key': self.alpaca_api_key,
            'secret_key': self.alpaca_secret_key,
            'base_url': self.alpaca_base_url,
            'data_url': self.alpaca_data_url
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'url': self.db_url
        }
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        return {
            'bot_token': self.telegram_bot_token,
            'chat_id': self.telegram_chat_id,
            'allowed_users': self.telegram_allowed_users,
            'enabled': bool(self.telegram_bot_token and self.telegram_chat_id)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system configuration status."""
        return {
            'paper_trading': self.paper_trading,
            'alpaca_configured': bool(self.alpaca_api_key and self.alpaca_secret_key),
            'database_configured': bool(self.db_host and self.db_user and self.db_password),
            'telegram_configured': bool(self.telegram_bot_token and self.telegram_chat_id),
            'log_level': self.log_level,
            'timestamp': datetime.now().isoformat(),
            'transaction_config': {
                'kill_switch_timeout': self.transaction_config.kill_switch_timeout,
                'max_retry_attempts': self.transaction_config.max_retry_attempts,
                'paper_trading_capital': self.transaction_config.paper_trading_capital,
                'max_position_size_percent': self.transaction_config.max_position_size_percent
            }
        }
    
    def validate_alpaca_credentials(self) -> bool:
        """Validate Alpaca API credentials."""
        try:
            import alpaca_trade_api as tradeapi
            
            api = tradeapi.REST(
                self.alpaca_api_key,
                self.alpaca_secret_key,
                self.alpaca_base_url,
                api_version='v2'
            )
            
            # Test API connection
            account = api.get_account()
            logger.info(f"✅ Alpaca credentials validated - Account status: {account.status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Alpaca credentials validation failed: {str(e)}")
            return False

# Global configuration instance
config = BrainConfig()
