"""
Unit tests for Laxmi-yantra Trading Manager
Blessed by Goddess Laxmi for Infinite Abundance 🙏
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from braintransactions.modules.laxmi_yantra import LaxmiYantra
from braintransactions.core.exceptions import (
    KillSwitchActiveError,
    OrderValidationError,
    TransactionExecutionError,
    InsufficientFundsError
)

class TestLaxmiYantraInitialization:
    """Test Laxmi-yantra initialization and configuration."""
    
    def test_initialization_success(self, laxmi_yantra):
        """Test successful initialization."""
        assert laxmi_yantra.module_name == "Laxmi-yantra"
        assert laxmi_yantra.is_initialized == True
        assert laxmi_yantra.config.paper_trading == True
    
    def test_get_system_status(self, laxmi_yantra):
        """Test system status retrieval."""
        status = laxmi_yantra.get_system_status()
        
        assert 'module_name' in status
        assert 'is_initialized' in status
        assert 'kill_switch_status' in status
        assert 'config_status' in status
        assert status['module_name'] == "Laxmi-yantra"
        assert status['is_initialized'] == True
    
    def test_get_account_info(self, laxmi_yantra):
        """Test account information retrieval."""
        account_info = laxmi_yantra.get_account_info()
        
        assert 'account_status' in account_info
        assert 'buying_power' in account_info
        assert 'cash' in account_info
        assert 'portfolio_value' in account_info
        assert account_info['account_status'] == 'ACTIVE'
        assert account_info['paper_trading'] == True

class TestLaxmiYantraTransactions:
    """Test transaction execution functionality."""
    
    def test_buy_transaction_success(self, laxmi_yantra, sample_transaction_data):
        """Test successful buy transaction."""
        result = laxmi_yantra.buy(
            ticker=sample_transaction_data['ticker'],
            quantity=sample_transaction_data['quantity'],
            strategy_name=sample_transaction_data['strategy_name']
        )
        
        assert result['success'] == True
        assert 'transaction_id' in result
        assert 'result' in result
        assert result['result']['action'] == 'buy'
        assert result['result']['ticker'] == sample_transaction_data['ticker']
        assert result['result']['quantity'] == sample_transaction_data['quantity']
    
    def test_sell_transaction_with_position(self, laxmi_yantra, sample_transaction_data):
        """Test sell transaction when position exists."""
        # First create a position by mocking get_position
        mock_position = {
            'strategy_name': sample_transaction_data['strategy_name'],
            'ticker': sample_transaction_data['ticker'],
            'quantity': 20,  # More than we want to sell
            'avg_entry_price': 150.0
        }
        
        with patch.object(laxmi_yantra.portfolio_manager, 'get_position', return_value=mock_position):
            result = laxmi_yantra.sell(
                ticker=sample_transaction_data['ticker'],
                quantity=sample_transaction_data['quantity'],
                strategy_name=sample_transaction_data['strategy_name']
            )
            
            assert result['success'] == True
            assert result['result']['action'] == 'sell'
    
    def test_sell_transaction_insufficient_position(self, laxmi_yantra, sample_transaction_data):
        """Test sell transaction with insufficient position."""
        # Mock insufficient position
        mock_position = {
            'strategy_name': sample_transaction_data['strategy_name'],
            'ticker': sample_transaction_data['ticker'],
            'quantity': 5,  # Less than we want to sell
            'avg_entry_price': 150.0
        }
        
        with patch.object(laxmi_yantra.portfolio_manager, 'get_position', return_value=mock_position):
            with pytest.raises(InsufficientFundsError):
                laxmi_yantra.sell(
                    ticker=sample_transaction_data['ticker'],
                    quantity=sample_transaction_data['quantity'],
                    strategy_name=sample_transaction_data['strategy_name']
                )
    
    def test_transaction_validation_errors(self, laxmi_yantra):
        """Test transaction validation errors."""
        # Test missing required fields
        with pytest.raises(OrderValidationError):
            laxmi_yantra.execute_transaction({})
        
        # Test invalid action
        with pytest.raises(OrderValidationError):
            laxmi_yantra.execute_transaction({
                'action': 'invalid_action',
                'ticker': 'AAPL',
                'quantity': 10
            })
        
        # Test invalid quantity
        with pytest.raises(OrderValidationError):
            laxmi_yantra.execute_transaction({
                'action': 'buy',
                'ticker': 'AAPL',
                'quantity': -10
            })
    
    def test_close_position_success(self, laxmi_yantra):
        """Test closing a position successfully."""
        # Mock existing position
        mock_position = {
            'strategy_name': 'test_strategy',
            'ticker': 'AAPL',
            'quantity': 10,
            'avg_entry_price': 150.0
        }
        
        with patch.object(laxmi_yantra.portfolio_manager, 'get_position', return_value=mock_position):
            result = laxmi_yantra.close_position('AAPL', 'test_strategy')
            
            assert result['success'] == True
            assert result['result']['action'] == 'sell'
            assert result['result']['quantity'] == 10
    
    def test_close_position_no_position(self, laxmi_yantra):
        """Test closing position when no position exists."""
        with patch.object(laxmi_yantra.portfolio_manager, 'get_position', return_value=None):
            result = laxmi_yantra.close_position('AAPL', 'test_strategy')
            
            assert result['success'] == True
            assert result['quantity_closed'] == 0

class TestLaxmiYantraKillSwitch:
    """Test kill switch functionality."""
    
    def test_kill_switch_blocks_transactions(self, laxmi_yantra, sample_transaction_data):
        """Test that kill switch blocks transactions."""
        # Activate kill switch
        laxmi_yantra.activate_kill_switch("Test activation")
        
        # Try to execute a transaction (should fail)
        with pytest.raises(KillSwitchActiveError):
            laxmi_yantra.buy(
                ticker=sample_transaction_data['ticker'],
                quantity=sample_transaction_data['quantity'],
                strategy_name=sample_transaction_data['strategy_name']
            )
    
    def test_kill_switch_deactivation(self, laxmi_yantra, sample_transaction_data):
        """Test kill switch deactivation allows transactions."""
        # Activate kill switch
        laxmi_yantra.activate_kill_switch("Test activation")
        assert laxmi_yantra.is_kill_switch_active() == True
        
        # Deactivate kill switch
        laxmi_yantra.deactivate_kill_switch()
        assert laxmi_yantra.is_kill_switch_active() == False
        
        # Transaction should now work
        result = laxmi_yantra.buy(
            ticker=sample_transaction_data['ticker'],
            quantity=sample_transaction_data['quantity'],
            strategy_name=sample_transaction_data['strategy_name']
        )
        assert result['success'] == True
    
    def test_emergency_stop(self, laxmi_yantra):
        """Test emergency stop functionality."""
        # Mock positions for emergency closure
        mock_positions = Mock()
        mock_positions.iterrows.return_value = [
            (0, {'ticker': 'AAPL', 'strategy_name': 'test_strategy', 'quantity': 10}),
            (1, {'ticker': 'GOOGL', 'strategy_name': 'test_strategy', 'quantity': 5})
        ]
        
        with patch.object(laxmi_yantra.portfolio_manager, 'get_all_positions', return_value=mock_positions):
            with patch.object(laxmi_yantra, 'close_position', return_value={'success': True}):
                result = laxmi_yantra.emergency_stop("Test emergency")
                
                assert result == True
                assert laxmi_yantra.is_kill_switch_active() == True

class TestLaxmiYantraHealthChecks:
    """Test health check functionality."""
    
    def test_health_check_all_pass(self, laxmi_yantra):
        """Test health check when all checks pass."""
        health = laxmi_yantra.health_check()
        
        assert 'healthy' in health
        assert 'checks' in health
        assert 'alpaca_api' in health['checks']
        assert 'portfolio_manager' in health['checks']
        assert 'order_manager' in health['checks']
    
    def test_module_health_checks(self, laxmi_yantra):
        """Test module-specific health checks."""
        checks = laxmi_yantra._perform_module_health_checks()
        
        assert 'alpaca_api' in checks
        assert 'portfolio_manager' in checks
        assert 'order_manager' in checks
        
        # All should pass with mocked dependencies
        for check_name, check_result in checks.items():
            assert check_result['status'] in ['pass', 'warn', 'fail']
            assert 'message' in check_result

class TestLaxmiYantraPortfolioIntegration:
    """Test portfolio management integration."""
    
    def test_get_portfolio_summary(self, laxmi_yantra):
        """Test portfolio summary retrieval."""
        mock_summary = {
            'strategy_name': 'test_strategy',
            'total_positions': 2,
            'total_quantity': 15,
            'avg_price': 150.0
        }
        
        with patch.object(laxmi_yantra.portfolio_manager, 'get_portfolio_summary', return_value=mock_summary):
            summary = laxmi_yantra.get_portfolio_summary()
            
            assert summary == mock_summary
    
    def test_portfolio_manager_initialization(self, laxmi_yantra):
        """Test that portfolio manager is properly initialized."""
        assert hasattr(laxmi_yantra, 'portfolio_manager')
        assert laxmi_yantra.portfolio_manager is not None
        
        # Test portfolio manager has kill switch capability
        assert hasattr(laxmi_yantra.portfolio_manager, 'activate_kill_switch')
        assert hasattr(laxmi_yantra.portfolio_manager, 'is_kill_switch_active')

class TestLaxmiYantraOrderIntegration:
    """Test order management integration."""
    
    def test_order_manager_initialization(self, laxmi_yantra):
        """Test that order manager is properly initialized."""
        assert hasattr(laxmi_yantra, 'order_manager')
        assert laxmi_yantra.order_manager is not None
        
        # Test order manager has kill switch capability
        assert hasattr(laxmi_yantra.order_manager, 'activate_kill_switch')
        assert hasattr(laxmi_yantra.order_manager, 'is_kill_switch_active')
    
    def test_order_storage_integration(self, laxmi_yantra, sample_transaction_data):
        """Test that orders are properly stored during transactions."""
        with patch.object(laxmi_yantra.order_manager, 'place_order', return_value=True) as mock_place_order:
            result = laxmi_yantra.buy(
                ticker=sample_transaction_data['ticker'],
                quantity=sample_transaction_data['quantity'],
                strategy_name=sample_transaction_data['strategy_name']
            )
            
            assert result['success'] == True
            # Verify that place_order was called
            mock_place_order.assert_called_once()
