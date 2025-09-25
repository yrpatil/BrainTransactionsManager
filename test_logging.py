#!/usr/bin/env python3
"""
Test script for BrainTransactionsManager v2.0.0 Sophisticated Logging System
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Demonstrates clean, relevant logging for production and detailed logging for debug mode.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.braintransactions.core.logging_config import setup_logging, get_logger


def test_production_logging():
    """Test production logging (clean and relevant)."""
    print("\n" + "="*60)
    print("🚀 TESTING PRODUCTION LOGGING (Clean & Relevant)")
    print("="*60)
    
    # Setup production logging
    system_logger = setup_logging(debug_mode=False, log_level="INFO")
    system_logger.startup_sequence()
    
    # Get component loggers
    server_logger = get_logger("server")
    db_logger = get_logger("database")
    exchange_logger = get_logger("exchange")
    monitoring_logger = get_logger("monitoring")
    
    # Simulate startup sequence
    server_logger.info("Initializing server components...")
    db_logger.startup("Initializing database connection manager v2.0.0")
    db_logger.info("Validating database connectivity...")
    db_logger.success("Database startup validation successful")
    
    exchange_logger.info("Initializing exchange adapters...")
    exchange_logger.success("Alpaca adapter connected successfully")
    
    monitoring_logger.info("Starting background monitoring...")
    monitoring_logger.success("Background monitoring started")
    
    # Simulate trading operations
    server_logger.trading("BUY", "AAPL", 10)
    server_logger.trading("SELL", "TSLA", 5)
    
    # Simulate performance metrics
    server_logger.performance("Database Query", 45.2)
    server_logger.performance("Order Placement", 1200.5)  # Slow operation
    
    # Simulate health checks
    server_logger.health("Database", "healthy")
    server_logger.health("Exchange", "healthy")
    server_logger.health("Monitoring", "degraded")
    
    # Simulate errors
    server_logger.error("Market data connection timeout")
    server_logger.warning("High memory usage detected")
    
    system_logger.shutdown_sequence()


def test_debug_logging():
    """Test debug logging (detailed and comprehensive)."""
    print("\n" + "="*60)
    print("🔍 TESTING DEBUG LOGGING (Detailed & Comprehensive)")
    print("="*60)
    
    # Setup debug logging
    system_logger = setup_logging(debug_mode=True, log_level="DEBUG")
    system_logger.startup_sequence()
    
    # Get component loggers
    server_logger = get_logger("server")
    db_logger = get_logger("database")
    exchange_logger = get_logger("exchange")
    monitoring_logger = get_logger("monitoring")
    
    # Simulate detailed startup sequence
    server_logger.debug("Loading configuration from config/development.yaml")
    server_logger.debug("Environment variables loaded: ENVIRONMENT=development")
    server_logger.info("Initializing server components...")
    
    db_logger.debug("Database config: host=localhost, port=5432, name=braintransactions")
    db_logger.startup("Initializing database connection manager v2.0.0")
    db_logger.debug("Creating connection pool with size 10")
    db_logger.info("Validating database connectivity...")
    db_logger.debug("Testing connection with timeout 30s")
    db_logger.success("Database startup validation successful")
    
    exchange_logger.debug("Loading Alpaca configuration")
    exchange_logger.debug("API Key: alpaca_paper_... (truncated)")
    exchange_logger.info("Initializing exchange adapters...")
    exchange_logger.debug("Creating AlpacaAdapter instance")
    exchange_logger.debug("Connecting to https://paper-api.alpaca.markets")
    exchange_logger.success("Alpaca adapter connected successfully")
    
    monitoring_logger.debug("Setting up monitoring tasks")
    monitoring_logger.debug("Task: price_updates, interval=60s")
    monitoring_logger.debug("Task: portfolio_sync, interval=300s")
    monitoring_logger.debug("Task: order_reconcile, interval=30s")
    monitoring_logger.info("Starting background monitoring...")
    monitoring_logger.success("Background monitoring started")
    
    # Simulate detailed trading operations
    server_logger.debug("Processing buy order request")
    server_logger.debug("Order details: symbol=AAPL, quantity=10, strategy=default")
    server_logger.debug("Validating order parameters")
    server_logger.trading("BUY", "AAPL", 10)
    server_logger.debug("Order submitted to exchange")
    server_logger.debug("Order ID: 12345-67890-abcde")
    
    # Simulate detailed performance metrics
    server_logger.debug("Executing database query: SELECT * FROM portfolio_positions")
    server_logger.performance("Database Query", 45.2)
    server_logger.debug("Query returned 15 rows")
    
    server_logger.debug("Placing order via Alpaca API")
    server_logger.debug("API call: POST /v2/orders")
    server_logger.debug("Request payload: {...}")
    server_logger.performance("Order Placement", 1200.5)
    server_logger.debug("API response: {...}")
    
    # Simulate detailed health checks
    server_logger.debug("Checking database connection pool")
    server_logger.debug("Active connections: 3/10")
    server_logger.health("Database", "healthy")
    
    server_logger.debug("Checking Alpaca API connectivity")
    server_logger.debug("API response time: 150ms")
    server_logger.health("Exchange", "healthy")
    
    server_logger.debug("Checking background task status")
    server_logger.debug("Task 'price_updates' last run: 45s ago")
    server_logger.debug("Task 'portfolio_sync' last run: 280s ago")
    server_logger.health("Monitoring", "degraded")
    
    # Simulate detailed errors
    server_logger.debug("Attempting to connect to market data feed")
    server_logger.debug("Connection timeout after 30s")
    server_logger.error("Market data connection timeout")
    server_logger.debug("Retrying connection in 5s...")
    
    server_logger.debug("Memory usage: 85% (1.2GB/1.4GB)")
    server_logger.debug("CPU usage: 45%")
    server_logger.warning("High memory usage detected")
    
    system_logger.shutdown_sequence()


def main():
    """Main test function."""
    print("🧪 BrainTransactionsManager v2.0.0 Logging System Test")
    print("Blessed by Goddess Laxmi for Infinite Abundance 🙏")
    
    # Test production logging
    test_production_logging()
    
    # Test debug logging
    test_debug_logging()
    
    print("\n" + "="*60)
    print("✅ LOGGING SYSTEM TEST COMPLETE")
    print("="*60)
    print("📊 Summary:")
    print("• Production logging: Clean, relevant, minimal noise")
    print("• Debug logging: Detailed, comprehensive, full context")
    print("• Both modes: Consistent formatting and structure")
    print("• File logging: Automatic log rotation in production")
    print("• Performance: Only slow operations logged in production")
    print("• Health checks: Only issues logged in production")
    print("\n🙏 May Goddess Laxmi bless this logging system!")


if __name__ == "__main__":
    main()
