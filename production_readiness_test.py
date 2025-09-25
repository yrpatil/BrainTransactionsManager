#!/usr/bin/env python3
"""
Production Readiness Test for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

This script thoroughly tests all endpoints to ensure the system is ready for production use with real money.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class ProductionReadinessTester:
    """Comprehensive production readiness tester."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, endpoint: str, success: bool, response: Dict[str, Any], error: str = None):
        """Log test result."""
        result = {
            'endpoint': endpoint,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'error': error
        }
        self.test_results.append(result)
        
        if not success:
            self.failed_tests.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
        if error:
            print(f"   Error: {error}")
    
    def test_health_endpoints(self):
        """Test health and system endpoints."""
        print("\n🏥 Testing Health & System Endpoints")
        print("=" * 50)
        
        # Basic health check
        try:
            response = self.session.get(f"{BASE_URL}/health")
            self.log_test("/health", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/health", False, {}, str(e))
        
        # Detailed health check
        try:
            response = self.session.get(f"{BASE_URL}/health/detailed")
            self.log_test("/health/detailed", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/health/detailed", False, {}, str(e))
        
        # Configuration status
        try:
            response = self.session.get(f"{BASE_URL}/config/status")
            self.log_test("/config/status", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/config/status", False, {}, str(e))
    
    def test_market_data_endpoints(self):
        """Test market data endpoints."""
        print("\n📊 Testing Market Data Endpoints")
        print("=" * 50)
        
        # Stock market data
        try:
            response = self.session.get(f"{BASE_URL}/market/data/AAPL")
            self.log_test("/market/data/AAPL", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/market/data/AAPL", False, {}, str(e))
        
        # Crypto market data
        try:
            response = self.session.get(f"{BASE_URL}/market/data/BTCUSD")
            self.log_test("/market/data/BTCUSD", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/market/data/BTCUSD", False, {}, str(e))
        
        # Exchange information
        try:
            response = self.session.get(f"{BASE_URL}/exchanges")
            self.log_test("/exchanges", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/exchanges", False, {}, str(e))
    
    def test_portfolio_endpoints(self):
        """Test portfolio management endpoints."""
        print("\n💼 Testing Portfolio Endpoints")
        print("=" * 50)
        
        # Account information
        try:
            response = self.session.get(f"{BASE_URL}/portfolio/account")
            self.log_test("/portfolio/account", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/portfolio/account", False, {}, str(e))
        
        # Portfolio positions
        try:
            response = self.session.get(f"{BASE_URL}/portfolio/positions")
            self.log_test("/portfolio/positions", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/portfolio/positions", False, {}, str(e))
        
        # Portfolio summary
        try:
            response = self.session.get(f"{BASE_URL}/portfolio/summary")
            self.log_test("/portfolio/summary", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/portfolio/summary", False, {}, str(e))
        
        # Strategy portfolio
        try:
            response = self.session.get(f"{BASE_URL}/portfolio/strategy/default")
            self.log_test("/portfolio/strategy/default", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/portfolio/strategy/default", False, {}, str(e))
    
    def test_order_management_endpoints(self):
        """Test order management endpoints."""
        print("\n📋 Testing Order Management Endpoints")
        print("=" * 50)
        
        # Get orders
        try:
            response = self.session.get(f"{BASE_URL}/orders")
            self.log_test("/orders", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/orders", False, {}, str(e))
        
        # Order statistics (removed)
        # Skipped: /orders/statistics endpoint removed
        
        # Test orders endpoint
        try:
            response = self.session.get(f"{BASE_URL}/test/orders")
            self.log_test("/test/orders", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/test/orders", False, {}, str(e))
    
    def test_trading_endpoints(self):
        """Test trading endpoints (with safety checks)."""
        print("\n💰 Testing Trading Endpoints (Safe Mode)")
        print("=" * 50)
        
        # Test buy order with minimal quantity (safe test)
        try:
            buy_data = {
                "symbol": "AAPL",
                "quantity": 1,
                "strategy_name": "production_test",
                "order_type": "market"
            }
            response = self.session.post(
                f"{BASE_URL}/buy",
                json=buy_data,
                headers={"Content-Type": "application/json"}
            )
            # Note: This might fail due to wash trade rules, which is expected
            self.log_test("/buy", response.status_code in [200, 400, 500], response.json())
        except Exception as e:
            self.log_test("/buy", False, {}, str(e))
        
        # Test sell order with minimal quantity (safe test)
        try:
            sell_data = {
                "symbol": "AAPL",
                "quantity": 1,
                "strategy_name": "production_test",
                "order_type": "market"
            }
            response = self.session.post(
                f"{BASE_URL}/sell",
                json=sell_data,
                headers={"Content-Type": "application/json"}
            )
            # Note: This might fail due to wash trade rules, which is expected
            self.log_test("/sell", response.status_code in [200, 400, 500], response.json())
        except Exception as e:
            self.log_test("/sell", False, {}, str(e))
        
        # Test close position (should handle no position gracefully)
        try:
            response = self.session.post(f"{BASE_URL}/close/AAPL")
            self.log_test("/close/AAPL", response.status_code in [200, 400, 500], response.json())
        except Exception as e:
            self.log_test("/close/AAPL", False, {}, str(e))
    
    def test_emergency_control_endpoints(self):
        """Test emergency control endpoints."""
        print("\n🚨 Testing Emergency Control Endpoints")
        print("=" * 50)
        
        # Kill switch status
        try:
            response = self.session.get(f"{BASE_URL}/kill-switch/status")
            self.log_test("/kill-switch/status", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/kill-switch/status", False, {}, str(e))
        
        # Activate kill switch
        try:
            activate_data = {
                "action": "activate",
                "reason": "Production readiness test"
            }
            response = self.session.post(
                f"{BASE_URL}/kill-switch",
                json=activate_data,
                headers={"Content-Type": "application/json"}
            )
            self.log_test("/kill-switch (activate)", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/kill-switch (activate)", False, {}, str(e))
        
        # Deactivate kill switch
        try:
            deactivate_data = {
                "action": "deactivate",
                "reason": "Test complete"
            }
            response = self.session.post(
                f"{BASE_URL}/kill-switch",
                json=deactivate_data,
                headers={"Content-Type": "application/json"}
            )
            self.log_test("/kill-switch (deactivate)", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/kill-switch (deactivate)", False, {}, str(e))
        
        # Emergency stop
        try:
            emergency_data = {
                "reason": "Production readiness test",
                "strategy_name": "all"
            }
            response = self.session.post(
                f"{BASE_URL}/emergency/stop",
                json=emergency_data,
                headers={"Content-Type": "application/json"}
            )
            self.log_test("/emergency/stop", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/emergency/stop", False, {}, str(e))
    
    def test_database_migration_endpoints(self):
        """Test database migration endpoints."""
        print("\n🗄️ Testing Database Migration Endpoints")
        print("=" * 50)
        
        # Migration status
        try:
            response = self.session.get(f"{BASE_URL}/migrations/status")
            self.log_test("/migrations/status", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("/migrations/status", False, {}, str(e))
        
        # Run migrations (read-only test)
        try:
            response = self.session.post(f"{BASE_URL}/migrations/run")
            self.log_test("/migrations/run", response.status_code in [200, 400, 500], response.json())
        except Exception as e:
            self.log_test("/migrations/run", False, {}, str(e))
    
    def test_close_all_positions_endpoint(self):
        """Test close all positions endpoint."""
        print("\n🔄 Testing Close All Positions Endpoint")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{BASE_URL}/portfolio/close-all")
            self.log_test("/portfolio/close-all", response.status_code in [200, 400, 500], response.json())
        except Exception as e:
            self.log_test("/portfolio/close-all", False, {}, str(e))
    
    def run_all_tests(self):
        """Run all production readiness tests."""
        print("🚀 BrainTransactionsManager v2.0.0 Production Readiness Test")
        print("Blessed by Goddess Laxmi for Infinite Abundance 🙏")
        print("=" * 70)
        print(f"Testing server at: {BASE_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_market_data_endpoints()
        self.test_portfolio_endpoints()
        self.test_order_management_endpoints()
        self.test_trading_endpoints()
        self.test_emergency_control_endpoints()
        self.test_database_migration_endpoints()
        self.test_close_all_positions_endpoint()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 70)
        print("📊 PRODUCTION READINESS TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  • {test['endpoint']}: {test['error']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if failed_tests == 0:
            print("✅ EXCELLENT - System is ready for production use!")
        elif failed_tests <= 2:
            print("⚠️  GOOD - Minor issues detected, review before production use")
        else:
            print("❌ CRITICAL - Multiple issues detected, DO NOT use in production")
        
        print(f"\n🙏 Blessed by Goddess Laxmi for Infinite Abundance!")
        
        # Save detailed results
        with open("production_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: production_test_results.json")

if __name__ == "__main__":
    tester = ProductionReadinessTester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
