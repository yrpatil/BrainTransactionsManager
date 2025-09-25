"""
Unified Configuration Management for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Single source of truth for all configuration with environment-based overrides.
Follows SRM principles: Simple, Reliable, Maintainable.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "braintransactions"
    user: str = ""  # Will be set during validation
    password: str = ""  # Will be set during validation
    schema: str = "laxmiyantra"
    pool_size: int = 10
    connection_timeout: int = 30
    
    @property
    def url(self) -> str:
        if self.password:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        else:
            return f"postgresql://{self.user}@{self.host}:{self.port}/{self.name}"


@dataclass
class TradingConfig:
    """Trading system configuration."""
    paper_trading: bool = True
    paper_trading_capital: float = 100000.0
    default_position_size: float = 100.0
    max_position_size_percent: float = 10.0
    max_daily_loss_percent: float = 5.0
    max_single_asset_allocation: float = 25.0
    kill_switch_timeout: int = 30
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class AlpacaConfig:
    """Alpaca API configuration."""
    api_key: str = ""
    secret_key: str = ""
    base_url: str = "https://paper-api.alpaca.markets"
    data_url: str = "https://data.alpaca.markets/v2"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.secret_key)


@dataclass
class SecurityConfig:
    """Security configuration."""
    api_rate_limit: int = 1000  # requests per hour
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    session_timeout: int = 3600  # seconds
    max_login_attempts: int = 5


@dataclass
class MonitoringConfig:
    """Monitoring and polling configuration."""
    price_poll_interval: int = 60  # seconds
    portfolio_sync_interval: int = 300  # seconds
    order_reconcile_interval: int = 30  # seconds
    health_check_interval: int = 30  # seconds
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_db: bool = False


class BrainConfig:
    """
    Unified configuration manager for v2.0.0.
    
    Features:
    • Single configuration file with environment overrides
    • Type-safe configuration sections
    • Environment-specific settings
    • Validation and defaults
    • Simple and maintainable
    """
    
    def __init__(self, config_file: Optional[str] = None, environment: str = "development"):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
            environment: Environment name (development, production, testing)
        """
        self.environment = environment
        self.config_file = config_file or f"config/{environment}.yaml"
        
        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.trading = TradingConfig()
        self.alpaca = AlpacaConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        
        # Load configuration
        self._load_configuration()
        self._validate_configuration()
        
        # Setup logging
        self._setup_logging()
    
    def _load_configuration(self):
        """Load configuration from file and environment variables."""
        # Load from YAML file if exists
        config_path = Path(self.config_file)
        file_config = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
        
        # Database configuration
        db_config = file_config.get('database', {})
        self.database.host = os.getenv('DB_HOST', db_config.get('host', self.database.host))
        self.database.port = int(os.getenv('DB_PORT', db_config.get('port', self.database.port)))
        self.database.name = os.getenv('DB_NAME', db_config.get('name', self.database.name))
        self.database.user = os.getenv('DB_USER', db_config.get('user', self.database.user))
        self.database.password = os.getenv('DB_PASSWORD', db_config.get('password', self.database.password))
        self.database.schema = os.getenv('DB_SCHEMA', db_config.get('schema', self.database.schema))
        self.database.pool_size = int(os.getenv('DB_POOL_SIZE', db_config.get('pool_size', self.database.pool_size)))
        
        # Trading configuration
        trading_config = file_config.get('trading', {})
        self.trading.paper_trading = os.getenv('PAPER_TRADING', str(trading_config.get('paper_trading', self.trading.paper_trading))).lower() == 'true'
        self.trading.paper_trading_capital = float(os.getenv('PAPER_TRADING_CAPITAL', trading_config.get('paper_trading_capital', self.trading.paper_trading_capital)))
        self.trading.max_position_size_percent = float(os.getenv('MAX_POSITION_SIZE_PERCENT', trading_config.get('max_position_size_percent', self.trading.max_position_size_percent)))
        
        # Alpaca configuration
        alpaca_config = file_config.get('alpaca', {})
        self.alpaca.api_key = os.getenv('ALPACA_API_KEY', alpaca_config.get('api_key', ''))
        self.alpaca.secret_key = os.getenv('ALPACA_SECRET_KEY', alpaca_config.get('secret_key', ''))
        self.alpaca.base_url = os.getenv('ALPACA_BASE_URL', alpaca_config.get('base_url', self.alpaca.base_url))
        self.alpaca.data_url = os.getenv('ALPACA_DATA_URL', alpaca_config.get('data_url', self.alpaca.data_url))
        
        # Security configuration
        security_config = file_config.get('security', {})
        self.security.api_rate_limit = int(os.getenv('API_RATE_LIMIT', security_config.get('api_rate_limit', self.security.api_rate_limit)))
        cors_origins = os.getenv('CORS_ORIGINS', ','.join(security_config.get('cors_origins', self.security.cors_origins)))
        self.security.cors_origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
        
        # Monitoring configuration
        monitoring_config = file_config.get('monitoring', {})
        self.monitoring.price_poll_interval = int(os.getenv('PRICE_POLL_INTERVAL', monitoring_config.get('price_poll_interval', self.monitoring.price_poll_interval)))
        self.monitoring.log_level = os.getenv('LOG_LEVEL', monitoring_config.get('log_level', self.monitoring.log_level))
        self.monitoring.log_to_db = os.getenv('LOG_TO_DB', str(monitoring_config.get('log_to_db', self.monitoring.log_to_db))).lower() == 'true'
    
    def _validate_configuration(self):
        """Validate critical configuration."""
        errors = []
        
        # Check required Alpaca credentials for non-testing environments
        if self.environment not in ['testing', 'development'] and not self.alpaca.is_configured:
            errors.append("Alpaca API credentials are required (ALPACA_API_KEY, ALPACA_SECRET_KEY)")
        
        # Validate database connection parameters (more flexible for development)
        if not self.database.host:
            errors.append("Database host is required")
        
        # For development, provide sensible defaults
        if self.environment == 'development':
            if not self.database.user:
                import os
                self.database.user = os.getenv('USER', 'postgres')
            if not self.database.password:
                self.database.password = ''  # Allow empty password for local dev
        else:
            # For production, require all parameters
            if not all([self.database.host, self.database.user, self.database.password]):
                errors.append("Database connection parameters are incomplete (host, user, password required)")
        
        # Validate trading parameters
        if self.trading.max_position_size_percent <= 0 or self.trading.max_position_size_percent > 100:
            errors.append("max_position_size_percent must be between 0 and 100")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        import logging
        
        # Set log level
        numeric_level = getattr(logging, self.monitoring.log_level.upper(), logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)
        
        # Optional file handler
        if self.monitoring.log_to_file:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / f"braintransactions_{self.environment}.log")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            root_logger.addHandler(file_handler)
        
        # Suppress noisy loggers
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('psycopg2').setLevel(logging.WARNING)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system configuration status."""
        return {
            'environment': self.environment,
            'config_file': self.config_file,
            'database_configured': bool(self.database.host and self.database.user),
            'alpaca_configured': self.alpaca.is_configured,
            'paper_trading': self.trading.paper_trading,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_config_template(self, output_file: str):
        """Create a configuration template file."""
        template = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'braintransactions',
                'user': 'brain_user',
                'password': 'brain_password',
                'schema': 'laxmiyantra',
                'pool_size': 10
            },
            'trading': {
                'paper_trading': True,
                'paper_trading_capital': 100000.0,
                'max_position_size_percent': 10.0,
                'max_daily_loss_percent': 5.0
            },
            'alpaca': {
                'api_key': '${ALPACA_API_KEY}',
                'secret_key': '${ALPACA_SECRET_KEY}',
                'base_url': 'https://paper-api.alpaca.markets'
            },
            'security': {
                'api_rate_limit': 1000,
                'cors_origins': ['http://localhost:3000']
            },
            'monitoring': {
                'price_poll_interval': 60,
                'log_level': 'INFO',
                'log_to_db': False
            }
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)


# Global configuration instance
config: Optional[BrainConfig] = None

def get_config(environment: str = None) -> BrainConfig:
    """Get global configuration instance."""
    global config
    if config is None:
        env = environment or os.getenv('ENVIRONMENT', 'development')
        config = BrainConfig(environment=env)
    return config


def init_config(config_file: str = None, environment: str = None) -> BrainConfig:
    """Initialize global configuration."""
    global config
    env = environment or os.getenv('ENVIRONMENT', 'development')
    config = BrainConfig(config_file=config_file, environment=env)
    return config
