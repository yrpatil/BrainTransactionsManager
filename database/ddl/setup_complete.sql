-- =================================================================
-- BrainTransactionsManager Complete Database Setup
-- Blessed by Goddess Laxmi for Infinite Abundance 🙏
-- =================================================================

-- Connect to postgres database to create new database
\c postgres;

-- Create the braintransactions database if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'braintransactions') THEN
        CREATE DATABASE braintransactions;
        RAISE NOTICE 'Database braintransactions created successfully!';
    ELSE
        RAISE NOTICE 'Database braintransactions already exists.';
    END IF;
END
$$;

-- Connect to the new database
\c braintransactions;

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create laxmiyantra schema
CREATE SCHEMA IF NOT EXISTS laxmiyantra;

-- Set search path to prioritize laxmiyantra schema
SET search_path TO laxmiyantra, public;

-- =================================================================
-- TABLE CREATION SECTION
-- =================================================================

-- Portfolio Positions Table
-- Tracks current holdings for each strategy and ticker
CREATE TABLE IF NOT EXISTS laxmiyantra.portfolio_positions (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    avg_entry_price DECIMAL(20, 8),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_name, ticker)
);

-- Order History Table
-- Complete lifecycle tracking of all orders
CREATE TABLE IF NOT EXISTS laxmiyantra.order_history (
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

-- Transaction Log Table
-- Audit trail for all system transactions
CREATE TABLE IF NOT EXISTS laxmiyantra.transaction_log (
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

-- OHLC Data Table (TimescaleDB Hypertable)
-- Market data storage optimized for time-series operations
CREATE TABLE IF NOT EXISTS laxmiyantra.ohlc_data (
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

-- Convert OHLC table to TimescaleDB hypertable
-- Only create hypertable if it doesn't already exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM _timescaledb_catalog.hypertable 
        WHERE schema_name = 'laxmiyantra' AND table_name = 'ohlc_data'
    ) THEN
        PERFORM create_hypertable('laxmiyantra.ohlc_data', 'timestamp');
        RAISE NOTICE 'TimescaleDB hypertable created for ohlc_data';
    ELSE
        RAISE NOTICE 'TimescaleDB hypertable already exists for ohlc_data';
    END IF;
END
$$;

-- Add unique constraint for OHLC data
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT constraint_name FROM information_schema.table_constraints 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'ohlc_data' 
        AND constraint_name = 'ohlc_data_unique_key'
    ) THEN
        ALTER TABLE laxmiyantra.ohlc_data 
        ADD CONSTRAINT ohlc_data_unique_key UNIQUE (timestamp, ticker, timeframe);
        RAISE NOTICE 'Unique constraint added to ohlc_data';
    ELSE
        RAISE NOTICE 'Unique constraint already exists on ohlc_data';
    END IF;
END
$$;

-- System Status Table
-- Track system health and kill switch status
CREATE TABLE IF NOT EXISTS laxmiyantra.system_status (
    id SERIAL PRIMARY KEY,
    component_name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status_message TEXT,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- INDEX CREATION SECTION
-- =================================================================

-- Portfolio Positions Indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_strategy_ticker 
ON laxmiyantra.portfolio_positions(strategy_name, ticker);

CREATE INDEX IF NOT EXISTS idx_portfolio_last_updated 
ON laxmiyantra.portfolio_positions(last_updated);

CREATE INDEX IF NOT EXISTS idx_portfolio_strategy 
ON laxmiyantra.portfolio_positions(strategy_name);

-- Order History Indexes
CREATE INDEX IF NOT EXISTS idx_order_strategy 
ON laxmiyantra.order_history(strategy_name);

CREATE INDEX IF NOT EXISTS idx_order_ticker 
ON laxmiyantra.order_history(ticker);

CREATE INDEX IF NOT EXISTS idx_order_status 
ON laxmiyantra.order_history(status);

CREATE INDEX IF NOT EXISTS idx_order_submitted_at 
ON laxmiyantra.order_history(submitted_at);

CREATE INDEX IF NOT EXISTS idx_order_strategy_ticker 
ON laxmiyantra.order_history(strategy_name, ticker);

CREATE INDEX IF NOT EXISTS idx_order_side_status 
ON laxmiyantra.order_history(side, status);

-- Transaction Log Indexes
CREATE INDEX IF NOT EXISTS idx_transaction_module 
ON laxmiyantra.transaction_log(module_name);

CREATE INDEX IF NOT EXISTS idx_transaction_status 
ON laxmiyantra.transaction_log(status);

CREATE INDEX IF NOT EXISTS idx_transaction_created_at 
ON laxmiyantra.transaction_log(created_at);

CREATE INDEX IF NOT EXISTS idx_transaction_type 
ON laxmiyantra.transaction_log(transaction_type);

-- OHLC Data Indexes
CREATE INDEX IF NOT EXISTS idx_ohlc_ticker_timeframe 
ON laxmiyantra.ohlc_data(ticker, timeframe);

CREATE INDEX IF NOT EXISTS idx_ohlc_ticker_timestamp 
ON laxmiyantra.ohlc_data(ticker, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_ohlc_timeframe_timestamp 
ON laxmiyantra.ohlc_data(timeframe, timestamp DESC);

-- System Status Indexes
CREATE INDEX IF NOT EXISTS idx_system_status_component 
ON laxmiyantra.system_status(component_name);

CREATE INDEX IF NOT EXISTS idx_system_status_active 
ON laxmiyantra.system_status(is_active);

-- =================================================================
-- TIMESCALEDB OPTIMIZATION SECTION
-- =================================================================

-- Set chunk time interval for OHLC data (1 day chunks)
SELECT set_chunk_time_interval('laxmiyantra.ohlc_data', INTERVAL '1 day');

-- Enable compression for OHLC data
DO $$
BEGIN
    BEGIN
        ALTER TABLE laxmiyantra.ohlc_data SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'ticker,timeframe'
        );
        RAISE NOTICE 'Compression enabled for ohlc_data';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Compression already enabled or error: %', SQLERRM;
    END;
END
$$;

-- Create compression policy (compress data older than 7 days)
DO $$
BEGIN
    BEGIN
        PERFORM add_compression_policy('laxmiyantra.ohlc_data', INTERVAL '7 days');
        RAISE NOTICE 'Compression policy added for ohlc_data';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Compression policy already exists or error: %', SQLERRM;
    END;
END
$$;

-- Create retention policy (keep data for 2 years)
DO $$
BEGIN
    BEGIN
        PERFORM add_retention_policy('laxmiyantra.ohlc_data', INTERVAL '2 years');
        RAISE NOTICE 'Retention policy added for ohlc_data';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Retention policy already exists or error: %', SQLERRM;
    END;
END
$$;

-- =================================================================
-- INITIAL DATA SECTION
-- =================================================================

-- Insert initial system status records
INSERT INTO laxmiyantra.system_status (component_name, is_active, status_message)
VALUES 
    ('laxmi_yantra', TRUE, 'Trading module initialized'),
    ('database', TRUE, 'Database connection healthy'),
    ('alpaca_api', TRUE, 'API connection ready')
ON CONFLICT (component_name) DO NOTHING;

-- =================================================================
-- VERIFICATION SECTION
-- =================================================================

-- Verify table creation
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'laxmiyantra';
    
    RAISE NOTICE 'Total tables created in laxmiyantra schema: %', table_count;
END
$$;

-- Verify indexes
DO $$
DECLARE
    index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes 
    WHERE schemaname = 'laxmiyantra';
    
    RAISE NOTICE 'Total indexes created in laxmiyantra schema: %', index_count;
END
$$;

-- Verify TimescaleDB hypertable
DO $$
DECLARE
    hypertable_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT FROM _timescaledb_catalog.hypertable 
        WHERE schema_name = 'laxmiyantra' AND table_name = 'ohlc_data'
    ) INTO hypertable_exists;
    
    IF hypertable_exists THEN
        RAISE NOTICE 'TimescaleDB hypertable verification: SUCCESS';
    ELSE
        RAISE NOTICE 'TimescaleDB hypertable verification: FAILED';
    END IF;
END
$$;

-- =================================================================
-- COMPLETION MESSAGE
-- =================================================================

SELECT 
    'BrainTransactionsManager database setup completed successfully!' as status,
    'May Goddess Laxmi bless this database with infinite abundance!' as blessing,
    NOW() as setup_timestamp;

-- Display schema information
\dn+ laxmiyantra

-- Display table information
\dt+ laxmiyantra.*

-- Display TimescaleDB information
SELECT * FROM timescaledb_information.hypertables WHERE hypertable_schema = 'laxmiyantra';

-- Show current database and schema
SELECT current_database(), current_schema();

\echo '================================================================='
\echo 'Database setup completed successfully!'
\echo 'Schema: laxmiyantra'
\echo 'Database: braintransactions'
\echo 'TimescaleDB: Enabled with hypertables'
\echo 'Divine blessing: Infinite abundance awaits! 🙏'
\echo '================================================================='
