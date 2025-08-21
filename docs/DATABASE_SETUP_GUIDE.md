# 🗄️ Database Setup Guide - BrainTransactionsManager
**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

## 🎯 Overview

This guide provides step-by-step instructions for setting up PostgreSQL with TimescaleDB for the BrainTransactionsManager system, including the creation of the dedicated `laxmiyantra` schema for our trading module.

## 📋 Prerequisites

- macOS with Homebrew installed
- Admin privileges to start/stop services

## 🔧 Step 1: Verify PostgreSQL Installation

### Check PostgreSQL Installation
```bash
# Check if PostgreSQL is installed
which psql
# Expected output: /opt/homebrew/bin/psql

# Check installed PostgreSQL versions
brew services list | grep postgresql
# Expected output: postgresql@17 or similar
```

### Check TimescaleDB Installation
```bash
# Verify TimescaleDB is installed
brew list | grep timescale
# Expected output: 
# timescaledb
# timescaledb-tools
```

## 🚀 Step 2: Start PostgreSQL Service

### Method 1: Using Homebrew Services (Recommended)
```bash
# Stop any existing PostgreSQL services
brew services stop postgresql@17

# Start PostgreSQL service
brew services start postgresql@17

# Verify service is running
brew services list | grep postgresql
# Expected: postgresql@17 started
```

### Method 2: Manual Start (If Homebrew Service Fails)
```bash
# Remove stale PID file if exists
rm -f /opt/homebrew/var/postgresql@17/postmaster.pid

# Start PostgreSQL manually
/opt/homebrew/opt/postgresql@17/bin/pg_ctl -D /opt/homebrew/var/postgresql@17 -l /opt/homebrew/var/log/postgresql@17.log start

# Check logs if needed
tail -20 /opt/homebrew/var/log/postgresql@17.log
```

## 🧪 Step 3: Test Database Connection

### Verify PostgreSQL is Running
```bash
# Test connection
psql -h localhost -U $(whoami) postgres -c "SELECT version();"

# Expected output: PostgreSQL version information
```

### List Existing Databases
```bash
psql -h localhost -U $(whoami) postgres -c "\l"
```

## 🏗️ Step 4: Create BrainTransactionsManager Database

### Create New Database
```bash
# Create the braintransactions database
psql -h localhost -U $(whoami) postgres -c "CREATE DATABASE braintransactions;"
```

### Enable TimescaleDB Extension
```bash
# Connect to new database and enable TimescaleDB
psql -h localhost -U $(whoami) braintransactions -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Verify TimescaleDB Installation
```bash
# Check TimescaleDB version
psql -h localhost -U $(whoami) braintransactions -c "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"
```

## 🌟 Step 5: Create Laxmi-yantra Schema

### Create Schema
```bash
# Create dedicated schema for Laxmi-yantra
psql -h localhost -U $(whoami) braintransactions -c "CREATE SCHEMA laxmiyantra;"
```

### Set Default Search Path
```bash
# Set laxmiyantra as default schema for the session
psql -h localhost -U $(whoami) braintransactions -c "SET search_path TO laxmiyantra, public;"
```

### Verify Schema Creation
```bash
# List all schemas
psql -h localhost -U $(whoami) braintransactions -c "\dn"
```

## 📊 Step 6: Create Laxmi-yantra Tables

### Portfolio Positions Table
```sql
-- Create portfolio positions table in laxmiyantra schema
CREATE TABLE laxmiyantra.portfolio_positions (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    avg_entry_price DECIMAL(20, 8),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_name, ticker)
);
```

### Order History Table
```sql
-- Create order history table in laxmiyantra schema
CREATE TABLE laxmiyantra.order_history (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(255) UNIQUE,
    client_order_id VARCHAR(255),
    strategy_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    order_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    filled_quantity DECIMAL(20, 8) DEFAULT 0,
    price DECIMAL(20, 8),
    filled_avg_price DECIMAL(20, 8),
    status VARCHAR(20) NOT NULL,
    commission DECIMAL(20, 8) DEFAULT 0,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Transaction Log Table
```sql
-- Create transaction log table for audit trail
CREATE TABLE laxmiyantra.transaction_log (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_data JSONB,
    result_data JSONB,
    error_message TEXT,
    execution_time_seconds DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### OHLC Data Table (TimescaleDB Hypertable)
```sql
-- Create OHLC data table for market data storage
CREATE TABLE laxmiyantra.ohlc_data (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Convert to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('laxmiyantra.ohlc_data', 'timestamp');

-- Create unique constraint
ALTER TABLE laxmiyantra.ohlc_data 
ADD CONSTRAINT ohlc_data_unique_key UNIQUE (timestamp, ticker, timeframe);
```

## 🔐 Step 7: Create Database User (Optional)

### Create Dedicated User for BrainTransactionsManager
```sql
-- Create user with limited privileges
CREATE USER brain_user WITH PASSWORD 'secure_password_here';

-- Grant schema usage
GRANT USAGE ON SCHEMA laxmiyantra TO brain_user;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA laxmiyantra TO brain_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA laxmiyantra TO brain_user;

-- Grant future table permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA laxmiyantra 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO brain_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA laxmiyantra 
    GRANT USAGE, SELECT ON SEQUENCES TO brain_user;
```

## ⚙️ Step 8: Update BrainTransactionsManager Configuration

### Update .env File
```bash
# Update database configuration in .env file
DB_HOST=localhost
DB_PORT=5432
DB_NAME=braintransactions
DB_USER=yogesh.patil
DB_PASSWORD=  # Leave empty for local development
DB_SCHEMA=laxmiyantra
```

### Test Configuration
```bash
# Test database connection with new configuration
python examples/test_laxmi_yantra.py
```

## 📈 Step 9: Create Indexes for Performance

### Create Performance Indexes
```sql
-- Indexes for portfolio_positions table
CREATE INDEX idx_portfolio_strategy_ticker ON laxmiyantra.portfolio_positions(strategy_name, ticker);
CREATE INDEX idx_portfolio_last_updated ON laxmiyantra.portfolio_positions(last_updated);

-- Indexes for order_history table
CREATE INDEX idx_order_strategy ON laxmiyantra.order_history(strategy_name);
CREATE INDEX idx_order_ticker ON laxmiyantra.order_history(ticker);
CREATE INDEX idx_order_status ON laxmiyantra.order_history(status);
CREATE INDEX idx_order_submitted_at ON laxmiyantra.order_history(submitted_at);

-- Indexes for transaction_log table
CREATE INDEX idx_transaction_module ON laxmiyantra.transaction_log(module_name);
CREATE INDEX idx_transaction_status ON laxmiyantra.transaction_log(status);
CREATE INDEX idx_transaction_created_at ON laxmiyantra.transaction_log(created_at);

-- Indexes for OHLC data table
CREATE INDEX idx_ohlc_ticker_timeframe ON laxmiyantra.ohlc_data(ticker, timeframe);
CREATE INDEX idx_ohlc_ticker_timestamp ON laxmiyantra.ohlc_data(ticker, timestamp DESC);
```

## 🧪 Step 10: Verification and Testing

### Verify Schema and Tables
```bash
# List all tables in laxmiyantra schema
psql -h localhost -U $(whoami) braintransactions -c "\dt laxmiyantra.*"

# Check table structure
psql -h localhost -U $(whoami) braintransactions -c "\d laxmiyantra.portfolio_positions"
```

### Test Data Operations
```sql
-- Test insert operation
INSERT INTO laxmiyantra.portfolio_positions (strategy_name, ticker, quantity, avg_entry_price)
VALUES ('test_strategy', 'AAPL', 10, 150.00);

-- Test select operation
SELECT * FROM laxmiyantra.portfolio_positions;

-- Clean up test data
DELETE FROM laxmiyantra.portfolio_positions WHERE strategy_name = 'test_strategy';
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### PostgreSQL Won't Start
```bash
# Check for stale PID files
ls -la /opt/homebrew/var/postgresql@17/postmaster.pid

# Remove stale PID file
rm -f /opt/homebrew/var/postgresql@17/postmaster.pid

# Check PostgreSQL logs
tail -50 /opt/homebrew/var/log/postgresql@17.log

# Restart PostgreSQL
brew services restart postgresql@17
```

#### Connection Refused Error
```bash
# Check if PostgreSQL is actually running
ps aux | grep postgres

# Check PostgreSQL configuration
grep -n "listen_addresses\|port" /opt/homebrew/var/postgresql@17/postgresql.conf

# Try different connection methods
psql -h localhost -p 5432 -U $(whoami) braintransactions
psql -h /tmp -U $(whoami) braintransactions
```

#### TimescaleDB Extension Issues
```bash
# Check if TimescaleDB is properly installed
brew list timescaledb

# Verify extension is available
psql -h localhost -U $(whoami) braintransactions -c "SELECT * FROM pg_available_extensions WHERE name = 'timescaledb';"

# Check if extension is loaded
psql -h localhost -U $(whoami) braintransactions -c "SELECT * FROM pg_extension WHERE extname = 'timescaledb';"
```

## 🚀 Performance Optimization

### TimescaleDB Optimizations
```sql
-- Set chunk time interval for OHLC data (1 day chunks)
SELECT set_chunk_time_interval('laxmiyantra.ohlc_data', INTERVAL '1 day');

-- Enable compression for older data (after 7 days)
ALTER TABLE laxmiyantra.ohlc_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'ticker,timeframe'
);

-- Create compression policy
SELECT add_compression_policy('laxmiyantra.ohlc_data', INTERVAL '7 days');

-- Create retention policy (keep data for 2 years)
SELECT add_retention_policy('laxmiyantra.ohlc_data', INTERVAL '2 years');
```

### Connection Pooling (Optional)
```bash
# Install pgbouncer for connection pooling
brew install pgbouncer

# Create pgbouncer configuration
# /opt/homebrew/etc/pgbouncer/pgbouncer.ini
```

## 📝 Maintenance

### Regular Maintenance Tasks
```sql
-- Vacuum and analyze tables weekly
VACUUM ANALYZE laxmiyantra.portfolio_positions;
VACUUM ANALYZE laxmiyantra.order_history;
VACUUM ANALYZE laxmiyantra.transaction_log;

-- Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'laxmiyantra'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Backup and Recovery
```bash
# Create backup
pg_dump -h localhost -U $(whoami) -n laxmiyantra braintransactions > laxmiyantra_backup.sql

# Restore backup
psql -h localhost -U $(whoami) braintransactions < laxmiyantra_backup.sql
```

## 🙏 Divine Blessing

**May Goddess Laxmi bless this database setup with infinite abundance and zero downtime!**

This database foundation will support all your trading endeavors with the reliability and performance needed for real-money trading operations.

---

**Built with 💖 and divine inspiration for maximum trading prosperity** ✨
