"""
System Tests for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Comprehensive system tests following SRM principles.
Tests essential functionality without overengineering.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import v2.0.0 components
from src.braintransactions import (
    BrainConfig, init_config,
    DatabaseManager, MigrationManager,
    ExchangeManager, BackgroundMonitor
)
from src.braintransactions.markets.base import AssetType, OrderSide, OrderType


class TestConfiguration:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = BrainConfig(environment='testing')
        
        assert config.environment == 'testing'
        assert config.database.host == 'localhost'
        assert config.trading.paper_trading == True
        assert hasattr(config, 'alpaca')
        assert hasattr(config, 'security')
        assert hasattr(config, 'monitoring')
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Should not raise for testing environment
        config = BrainConfig(environment='testing')
        assert config is not None
    
    def test_system_status(self):
        """Test system status reporting."""
        config = BrainConfig(environment='testing')
        status = config.get_system_status()
        
        assert 'environment' in status
        assert 'database_configured' in status
        assert 'timestamp' in status


class TestDatabaseManager:
    """Test database management."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return BrainConfig(environment='testing')
    
    @pytest.fixture
    def db_manager(self, config):
        """Database manager instance."""
        return DatabaseManager(config)
    
    @patch('psycopg2.connect')
    def test_connection_params(self, mock_connect, db_manager):
        """Test connection parameter generation."""
        params = db_manager.get_connection_params()
        
        assert 'host' in params
        assert 'port' in params
        assert 'database' in params
        assert 'user' in params
        assert 'password' in params
    
    @patch('psycopg2.connect')
    def test_health_status(self, mock_connect, db_manager):
        """Test health status reporting."""
        # Mock successful connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'test_value': 1}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        status = db_manager.get_health_status()
        
        assert 'status' in status
        assert 'timestamp' in status


class TestExchangeManager:
    """Test exchange management."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        config = BrainConfig(environment='testing')
        # Mock Alpaca credentials for testing
        config.alpaca.api_key = 'test_key'
        config.alpaca.secret_key = 'test_secret'
        return config
    
    @pytest.fixture
    def exchange_manager(self, config):
        """Exchange manager instance."""
        return ExchangeManager(config)
    
    def test_adapter_registration(self, exchange_manager):
        """Test adapter registration."""
        assert 'alpaca' in exchange_manager.adapters
        assert exchange_manager.default_adapter == 'alpaca'
    
    def test_get_adapter(self, exchange_manager):
        """Test adapter selection."""
        # Test default adapter
        adapter = exchange_manager.get_adapter()
        assert adapter is not None
        
        # Test specific exchange
        adapter = exchange_manager.get_adapter('alpaca')
        assert adapter is not None
        assert adapter.name == 'alpaca_unified'
    
    def test_supported_exchanges(self, exchange_manager):
        """Test supported exchanges listing."""
        exchanges = exchange_manager.get_supported_exchanges()
        assert isinstance(exchanges, list)
        assert 'alpaca' in exchanges
    
    def test_adapter_info(self, exchange_manager):
        """Test adapter information."""
        info = exchange_manager.get_adapter_info()
        assert isinstance(info, dict)
        assert 'alpaca' in info


class TestBackgroundMonitor:
    """Test background monitoring."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return BrainConfig(environment='testing')
    
    @pytest.fixture
    def mock_exchange_manager(self):
        """Mock exchange manager."""
        mock = Mock(spec=ExchangeManager)
        mock.get_positions = AsyncMock(return_value=[])
        mock.get_account_info = AsyncMock(return_value={'portfolio_value': 10000})
        mock.health_check = AsyncMock(return_value={'status': 'healthy'})
        return mock
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        mock = Mock(spec=DatabaseManager)
        mock.get_health_status = Mock(return_value={'status': 'healthy'})
        mock.execute_action = Mock(return_value=True)
        mock.execute_query = Mock(return_value=[])
        return mock
    
    @pytest.fixture
    def monitor(self, config, mock_exchange_manager, mock_db_manager):
        """Background monitor instance."""
        return BackgroundMonitor(config, mock_exchange_manager, mock_db_manager)
    
    def test_task_registration(self, monitor):
        """Test task registration."""
        assert len(monitor.tasks) > 0
        assert 'price_updates' in monitor.tasks
        assert 'portfolio_sync' in monitor.tasks
        assert 'kpi_calculation' in monitor.tasks
    
    def test_monitoring_status(self, monitor):
        """Test monitoring status reporting."""
        status = monitor.get_monitoring_status()
        
        assert 'is_running' in status
        assert 'total_tasks' in status
        assert 'tasks' in status
        assert 'timestamp' in status
    
    @pytest.mark.asyncio
    async def test_start_stop(self, monitor):
        """Test monitor start/stop."""
        # Start monitoring
        await monitor.start()
        assert monitor.is_running == True
        
        # Stop monitoring
        await monitor.stop()
        assert monitor.is_running == False


class TestMigrationManager:
    """Test migration management."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return BrainConfig(environment='testing')
    
    @pytest.fixture
    def migration_manager(self, config):
        """Migration manager instance."""
        return MigrationManager(config)
    
    def test_initialization(self, migration_manager):
        """Test migration manager initialization."""
        assert migration_manager.config is not None
        assert migration_manager.migrations_dir.exists()
    
    def test_validation(self, migration_manager):
        """Test migration validation."""
        validation = migration_manager.validate_migrations()
        
        assert 'status' in validation
        assert 'timestamp' in validation


@pytest.mark.integration
class TestSystemIntegration:
    """Integration tests for complete system."""
    
    @pytest.fixture
    def config(self):
        """Integration test configuration."""
        config = BrainConfig(environment='testing')
        # Mock credentials
        config.alpaca.api_key = 'test_key'
        config.alpaca.secret_key = 'test_secret'
        return config
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, config):
        """Test complete system initialization."""
        # This would be a more comprehensive test
        # For now, just test component creation
        
        db_manager = DatabaseManager(config)
        exchange_manager = ExchangeManager(config)
        
        assert db_manager is not None
        assert exchange_manager is not None
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self, config):
        """Test integrated health checking."""
        db_manager = DatabaseManager(config)
        exchange_manager = ExchangeManager(config)
        
        # Mock database connection for testing
        with patch('psycopg2.connect'):
            db_health = db_manager.get_health_status()
            exchange_health = await exchange_manager.health_check()
        
        assert 'status' in db_health
        assert 'adapters' in exchange_health


# Performance tests
@pytest.mark.performance
class TestPerformance:
    """Performance tests for critical paths."""
    
    @pytest.fixture
    def config(self):
        """Performance test configuration."""
        return BrainConfig(environment='testing')
    
    def test_config_loading_performance(self):
        """Test configuration loading performance."""
        import time
        
        start_time = time.time()
        config = BrainConfig(environment='testing')
        load_time = time.time() - start_time
        
        # Should load in under 100ms
        assert load_time < 0.1
        assert config is not None


# Error handling tests
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_environment(self):
        """Test handling of invalid environment."""
        # Should not crash, should use defaults
        config = BrainConfig(environment='nonexistent')
        assert config is not None
    
    @patch('psycopg2.connect')
    def test_database_connection_failure(self, mock_connect):
        """Test database connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")
        
        config = BrainConfig(environment='testing')
        db_manager = DatabaseManager(config)
        
        # Should not crash, should return False
        result = db_manager.check_connection()
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
