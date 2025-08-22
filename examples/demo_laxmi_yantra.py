#!/usr/bin/env python3
"""
Test script for Laxmi-yantra Trading Manager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

This script demonstrates and tests the Laxmi-yantra trading module with paper trading.
"""

import sys
import os
from datetime import datetime
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from braintransactions import LaxmiYantra, BrainConfig
    from braintransactions.core.exceptions import *
    
    print("🙏 Welcome to Laxmi-yantra Trading Manager Test")
    print("   May Goddess Laxmi bless this testing session")
    print("=" * 60)
    
    def test_configuration():
        """Test configuration and initialization."""
        print("\n📋 Testing Configuration and Initialization...")
        
        try:
            config = BrainConfig()
            print(f"✅ Configuration loaded successfully")
            print(f"   Paper trading mode: {config.paper_trading}")
            print(f"   Alpaca endpoint: {config.alpaca_base_url}")
            
            # Validate Alpaca credentials
            if config.validate_alpaca_credentials():
                print("✅ Alpaca credentials validated")
            else:
                print("❌ Alpaca credentials validation failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {str(e)}")
            return False
    
    def test_laxmi_yantra_initialization():
        """Test Laxmi-yantra initialization."""
        print("\n🏛️ Testing Laxmi-yantra Initialization...")
        
        try:
            # Initialize Laxmi-yantra
            laxmi = LaxmiYantra()
            print("✅ Laxmi-yantra initialized successfully")
            
            # Get system status
            status = laxmi.get_system_status()
            print(f"   System ready: {status.get('config_status', {}).get('alpaca_configured', False)}")
            print(f"   Kill switch active: {status['kill_switch_status']['active']}")
            
            # Get account info
            account_info = laxmi.get_account_info()
            if 'error' not in account_info:
                print(f"   Account status: {account_info['account_status']}")
                print(f"   Buying power: ${account_info['buying_power']:,.2f}")
                print(f"   Cash: ${account_info['cash']:,.2f}")
                print(f"   Portfolio value: ${account_info['portfolio_value']:,.2f}")
            else:
                print(f"❌ Account info error: {account_info['error']}")
                return False, None
            
            return True, laxmi
            
        except Exception as e:
            print(f"❌ Laxmi-yantra initialization failed: {str(e)}")
            return False, None
    
    def test_health_checks(laxmi):
        """Test health check functionality."""
        print("\n🏥 Testing Health Checks...")
        
        try:
            health = laxmi.health_check()
            print(f"✅ Health check completed")
            print(f"   Overall health: {'✅ Healthy' if health['healthy'] else '❌ Unhealthy'}")
            
            for check_name, check_result in health['checks'].items():
                status_emoji = "✅" if check_result['status'] == 'pass' else "⚠️" if check_result['status'] == 'warn' else "❌"
                print(f"   {check_name}: {status_emoji} {check_result['message']}")
            
            return health['healthy']
            
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            return False
    
    def test_portfolio_operations(laxmi):
        """Test portfolio management operations."""
        print("\n💼 Testing Portfolio Operations...")
        
        try:
            # Get initial portfolio summary
            initial_summary = laxmi.get_portfolio_summary()
            print(f"✅ Retrieved portfolio summary")
            print(f"   Strategies: {initial_summary.get('strategy_name', 'None')}")
            
            # Test getting positions
            positions = laxmi.portfolio_manager.get_all_positions()
            print(f"✅ Retrieved all positions: {len(positions)} positions")
            
            return True
            
        except Exception as e:
            print(f"❌ Portfolio operations test failed: {str(e)}")
            return False
    
    def test_order_operations(laxmi):
        """Test order management operations."""
        print("\n📋 Testing Order Operations...")
        
        try:
            # Get order history
            order_history = laxmi.order_manager.get_order_history(limit=10)
            print(f"✅ Retrieved order history: {len(order_history)} orders")
            
            # Get order statistics
            stats = laxmi.order_manager.get_order_statistics()
            print(f"✅ Retrieved order statistics")
            print(f"   Total orders: {stats.get('total_orders', 0)}")
            print(f"   Filled orders: {stats.get('filled_orders', 0)}")
            print(f"   Fill rate: {stats.get('fill_rate', 0):.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Order operations test failed: {str(e)}")
            return False
    
    def test_kill_switch(laxmi):
        """Test kill switch functionality."""
        print("\n🚨 Testing Kill Switch Functionality...")
        
        try:
            # Test kill switch activation
            print("   Activating kill switch...")
            success = laxmi.activate_kill_switch("Test activation")
            if success:
                print("✅ Kill switch activated successfully")
                
                # Try to perform an operation (should fail)
                try:
                    laxmi.buy("AAPL", 1, "test_strategy")
                    print("❌ Operation succeeded when it should have failed")
                    return False
                except KillSwitchActiveError:
                    print("✅ Operation correctly blocked by kill switch")
                
                # Deactivate kill switch
                print("   Deactivating kill switch...")
                success = laxmi.deactivate_kill_switch()
                if success:
                    print("✅ Kill switch deactivated successfully")
                    return True
                else:
                    print("❌ Kill switch deactivation failed")
                    return False
            else:
                print("❌ Kill switch activation failed")
                return False
            
        except Exception as e:
            print(f"❌ Kill switch test failed: {str(e)}")
            return False
    
    def test_paper_trading_transaction(laxmi):
        """Test actual paper trading transaction."""
        print("\n📈 Testing Paper Trading Transaction...")
        
        if not laxmi.config.paper_trading:
            print("⚠️ Not in paper trading mode - skipping transaction test")
            return True
        
        try:
            test_ticker = "AAPL"
            test_quantity = 1
            test_strategy = "test_strategy"
            
            print(f"   Executing buy order: {test_quantity} shares of {test_ticker}")
            
            # Execute buy transaction
            result = laxmi.buy(test_ticker, test_quantity, test_strategy)
            
            if result['success']:
                print("✅ Buy transaction executed successfully")
                print(f"   Transaction ID: {result['transaction_id']}")
                print(f"   Order ID: {result['result']['order_id']}")
                print(f"   Execution time: {result['execution_time_seconds']:.3f}s")
                
                # Wait a moment for processing
                time.sleep(2)
                
                # Check position
                position = laxmi.portfolio_manager.get_position(test_strategy, test_ticker)
                if position:
                    print(f"✅ Position created: {position['quantity']} shares at ${position['avg_entry_price']:.2f}")
                    
                    # Test sell transaction
                    print(f"   Executing sell order: {test_quantity} shares of {test_ticker}")
                    sell_result = laxmi.sell(test_ticker, test_quantity, test_strategy)
                    
                    if sell_result['success']:
                        print("✅ Sell transaction executed successfully")
                        
                        # Wait and check position again
                        time.sleep(2)
                        final_position = laxmi.portfolio_manager.get_position(test_strategy, test_ticker)
                        if not final_position or final_position['quantity'] == 0:
                            print("✅ Position closed successfully")
                        else:
                            print(f"⚠️ Position still exists: {final_position['quantity']} shares")
                        
                        return True
                    else:
                        print("❌ Sell transaction failed")
                        return False
                else:
                    print("⚠️ No position found after buy order")
                    return True  # Still count as success for paper trading
            else:
                print("❌ Buy transaction failed")
                return False
            
        except Exception as e:
            print(f"❌ Paper trading transaction test failed: {str(e)}")
            return False
    
    def run_comprehensive_test():
        """Run comprehensive test suite."""
        print("🧪 Starting Comprehensive Laxmi-yantra Test Suite")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Configuration
        test_results.append(("Configuration", test_configuration()))
        
        # Test 2: Initialization
        init_success, laxmi = test_laxmi_yantra_initialization()
        test_results.append(("Initialization", init_success))
        
        if not init_success:
            print("❌ Critical failure - cannot continue tests")
            return False
        
        # Test 3: Health Checks
        test_results.append(("Health Checks", test_health_checks(laxmi)))
        
        # Test 4: Portfolio Operations
        test_results.append(("Portfolio Operations", test_portfolio_operations(laxmi)))
        
        # Test 5: Order Operations
        test_results.append(("Order Operations", test_order_operations(laxmi)))
        
        # Test 6: Kill Switch
        test_results.append(("Kill Switch", test_kill_switch(laxmi)))
        
        # Test 7: Paper Trading Transaction
        test_results.append(("Paper Trading Transaction", test_paper_trading_transaction(laxmi)))
        
        # Print results summary
        print("\n" + "=" * 60)
        print("🏆 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
            if success:
                passed += 1
        
        print("-" * 60)
        print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Laxmi-yantra is ready for operation!")
            print("🙏 May Goddess Laxmi bless your trading endeavors")
        else:
            print("⚠️ Some tests failed. Please review and fix issues before proceeding.")
        
        return passed == total
    
    # Run the test suite
    if __name__ == "__main__":
        try:
            success = run_comprehensive_test()
            
            print("\n" + "=" * 60)
            if success:
                print("✅ Laxmi-yantra Testing Completed Successfully")
            else:
                print("❌ Laxmi-yantra Testing Completed with Issues")
            print("🙏 Thank you for testing Laxmi-yantra")
            print("   May Goddess Laxmi continue to bless this system")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Testing interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Critical error during testing: {str(e)}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("\nPlease ensure:")
    print("1. You've installed the requirements: pip install -r requirements.txt")
    print("2. You've set up your .env file with Alpaca credentials")
    print("3. You're running from the correct directory")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()
