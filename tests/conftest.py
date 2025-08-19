"""
Pytest configuration for BrainTransactionsManager tests
Blessed by Goddess Laxmi for Infinite Abundance 🙏
"""

import pytest
import os
import sys
from typing import Generator
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from braintransactions.core.config import BrainConfig
from braintransactions.modules.laxmi_yantra import LaxmiYantra

@pytest.fixture
def mock_config() -> BrainConfig:
    """Create a mock configuration for testing."""
    with patch.dict(os.environ, {
        'ALPACA_API_KEY': 'test_api_key',
        'ALPACA_SECRET_KEY': 'test_secret_key',
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_braintransactions',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'PAPER_TRADING': 'true',
    }):
        # Mock the Alpaca credential validation
        with patch('braintransactions.core.config.BrainConfig.validate_alpaca_credentials', return_value=True):
            config = BrainConfig()
            yield config

@pytest.fixture
def mock_alpaca_api():
    """Mock Alpaca API for testing."""
    mock_api = Mock()
    
    # Mock account info
    mock_account = Mock()
    mock_account.status = 'ACTIVE'
    mock_account.buying_power = 100000.0
    mock_account.cash = 100000.0
    mock_account.portfolio_value = 100000.0
    mock_account.daytrading_buying_power = 100000.0
    mock_account.equity = 100000.0
    
    mock_api.get_account.return_value = mock_account
    
    # Mock order submission
    mock_order = Mock()
    mock_order.id = 'test_order_123'
    mock_order.client_order_id = 'test_client_order_123'
    mock_order.status = 'accepted'
    mock_order.asset_class = 'us_equity'
    mock_order.time_in_force = 'day'
    mock_order.submitted_at = None
    mock_order.limit_price = None
    
    mock_api.submit_order.return_value = mock_order
    
    # Mock bars data
    mock_bars = Mock()
    mock_bars.df = Mock()
    mock_bars.df.empty = True
    mock_api.get_bars.return_value = mock_bars
    
    return mock_api

@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('braintransactions.database.connection.DatabaseManager') as mock_db_class:
        mock_db = Mock()
        mock_db.check_connection.return_value = True
        mock_db.execute_single.return_value = None
        mock_db.execute_query.return_value = []
        mock_db.execute_action.return_value = True
        mock_db.create_tables.return_value = True
        mock_db_class.return_value = mock_db
        yield mock_db

@pytest.fixture
def laxmi_yantra(mock_config, mock_alpaca_api, mock_database) -> Generator[LaxmiYantra, None, None]:
    """Create a LaxmiYantra instance for testing."""
    with patch('alpaca_trade_api.REST', return_value=mock_alpaca_api):
        laxmi = LaxmiYantra(mock_config)
        yield laxmi

@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        'action': 'buy',
        'ticker': 'AAPL',
        'quantity': 10,
        'strategy_name': 'test_strategy',
        'order_type': 'market'
    }

@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        'order_id': 'test_order_123',
        'client_order_id': 'test_client_order_123',
        'strategy_name': 'test_strategy',
        'ticker': 'AAPL',
        'side': 'buy',
        'order_type': 'market',
        'quantity': 10,
        'price': None,
        'status': 'accepted'
    }
