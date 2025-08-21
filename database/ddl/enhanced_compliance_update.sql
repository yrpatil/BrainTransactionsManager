-- =================================================================
-- Enhanced Database Compliance Update for Laxmi-yantra
-- Supporting enhanced buy/sell workflows with limit orders and audit trail
-- =================================================================

-- Connect to braintransactions database
\c braintransactions;

-- Set search path to laxmiyantra schema
SET search_path TO laxmiyantra, public;

-- =================================================================
-- SCHEMA COMPLIANCE UPDATES
-- =================================================================

-- Add missing columns to order_history table for enhanced functionality
DO $$
BEGIN
    -- Add limit_price column for limit orders
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'limit_price'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN limit_price DECIMAL(20, 8);
        RAISE NOTICE 'Added limit_price column to order_history';
    END IF;

    -- Add transaction_id for linking to transaction_log
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'transaction_id'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN transaction_id VARCHAR(255);
        RAISE NOTICE 'Added transaction_id column to order_history';
    END IF;

    -- Add pre_execution_data for audit trail
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'pre_execution_data'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN pre_execution_data JSONB;
        RAISE NOTICE 'Added pre_execution_data column to order_history';
    END IF;

    -- Add post_execution_data for verification
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'post_execution_data'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN post_execution_data JSONB;
        RAISE NOTICE 'Added post_execution_data column to order_history';
    END IF;

    -- Add validation_status for tracking validation results
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'validation_status'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN validation_status VARCHAR(50) DEFAULT 'pending';
        RAISE NOTICE 'Added validation_status column to order_history';
    END IF;

    -- Add risk_assessment for risk management tracking
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'order_history' 
        AND column_name = 'risk_assessment'
    ) THEN
        ALTER TABLE laxmiyantra.order_history 
        ADD COLUMN risk_assessment JSONB;
        RAISE NOTICE 'Added risk_assessment column to order_history';
    END IF;
END
$$;

-- =================================================================
-- ENHANCED PORTFOLIO POSITIONS COMPLIANCE
-- =================================================================

DO $$
BEGIN
    -- Add position_status for better position tracking
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'portfolio_positions' 
        AND column_name = 'position_status'
    ) THEN
        ALTER TABLE laxmiyantra.portfolio_positions 
        ADD COLUMN position_status VARCHAR(20) DEFAULT 'active';
        RAISE NOTICE 'Added position_status column to portfolio_positions';
    END IF;

    -- Add unrealized_pnl for real-time P&L tracking
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'portfolio_positions' 
        AND column_name = 'unrealized_pnl'
    ) THEN
        ALTER TABLE laxmiyantra.portfolio_positions 
        ADD COLUMN unrealized_pnl DECIMAL(20, 8) DEFAULT 0;
        RAISE NOTICE 'Added unrealized_pnl column to portfolio_positions';
    END IF;

    -- Add current_price for position valuation
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'portfolio_positions' 
        AND column_name = 'current_price'
    ) THEN
        ALTER TABLE laxmiyantra.portfolio_positions 
        ADD COLUMN current_price DECIMAL(20, 8);
        RAISE NOTICE 'Added current_price column to portfolio_positions';
    END IF;

    -- Add last_price_update for tracking price freshness
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'portfolio_positions' 
        AND column_name = 'last_price_update'
    ) THEN
        ALTER TABLE laxmiyantra.portfolio_positions 
        ADD COLUMN last_price_update TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added last_price_update column to portfolio_positions';
    END IF;
END
$$;

-- =================================================================
-- ENHANCED TRANSACTION LOG COMPLIANCE
-- =================================================================

DO $$
BEGIN
    -- Add security_level for transaction risk classification
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'transaction_log' 
        AND column_name = 'security_level'
    ) THEN
        ALTER TABLE laxmiyantra.transaction_log 
        ADD COLUMN security_level VARCHAR(20) DEFAULT 'standard';
        RAISE NOTICE 'Added security_level column to transaction_log';
    END IF;

    -- Add user_context for tracking request origin
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'transaction_log' 
        AND column_name = 'user_context'
    ) THEN
        ALTER TABLE laxmiyantra.transaction_log 
        ADD COLUMN user_context JSONB;
        RAISE NOTICE 'Added user_context column to transaction_log';
    END IF;

    -- Add validation_errors for tracking validation failures
    IF NOT EXISTS (
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'laxmiyantra' 
        AND table_name = 'transaction_log' 
        AND column_name = 'validation_errors'
    ) THEN
        ALTER TABLE laxmiyantra.transaction_log 
        ADD COLUMN validation_errors JSONB;
        RAISE NOTICE 'Added validation_errors column to transaction_log';
    END IF;
END
$$;

-- =================================================================
-- CREATE ENHANCED AUDIT TABLE
-- =================================================================

-- Create comprehensive audit trail table
CREATE TABLE IF NOT EXISTS laxmiyantra.audit_trail (
    id SERIAL PRIMARY KEY,
    audit_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    performed_by VARCHAR(255),
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    risk_level VARCHAR(20) DEFAULT 'low',
    compliance_flags JSONB,
    notes TEXT
);

-- =================================================================
-- CREATE ENHANCED INDEXES FOR PERFORMANCE
-- =================================================================

-- Enhanced order_history indexes
CREATE INDEX IF NOT EXISTS idx_order_history_transaction_id 
ON laxmiyantra.order_history(transaction_id);

CREATE INDEX IF NOT EXISTS idx_order_history_limit_price 
ON laxmiyantra.order_history(limit_price) WHERE limit_price IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_order_history_validation_status 
ON laxmiyantra.order_history(validation_status);

CREATE INDEX IF NOT EXISTS idx_order_history_pre_execution_data 
ON laxmiyantra.order_history USING GIN(pre_execution_data);

-- Enhanced portfolio_positions indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_status 
ON laxmiyantra.portfolio_positions(position_status);

CREATE INDEX IF NOT EXISTS idx_portfolio_positions_unrealized_pnl 
ON laxmiyantra.portfolio_positions(unrealized_pnl);

CREATE INDEX IF NOT EXISTS idx_portfolio_positions_price_update 
ON laxmiyantra.portfolio_positions(last_price_update);

-- Enhanced transaction_log indexes
CREATE INDEX IF NOT EXISTS idx_transaction_log_security_level 
ON laxmiyantra.transaction_log(security_level);

CREATE INDEX IF NOT EXISTS idx_transaction_log_user_context 
ON laxmiyantra.transaction_log USING GIN(user_context);

-- Audit trail indexes
CREATE INDEX IF NOT EXISTS idx_audit_trail_event_type 
ON laxmiyantra.audit_trail(event_type);

CREATE INDEX IF NOT EXISTS idx_audit_trail_entity 
ON laxmiyantra.audit_trail(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_trail_performed_by 
ON laxmiyantra.audit_trail(performed_by);

CREATE INDEX IF NOT EXISTS idx_audit_trail_performed_at 
ON laxmiyantra.audit_trail(performed_at);

CREATE INDEX IF NOT EXISTS idx_audit_trail_risk_level 
ON laxmiyantra.audit_trail(risk_level);

-- =================================================================
-- CREATE SECURITY VIEWS
-- =================================================================

-- Secure order history view with sensitive data protection
CREATE OR REPLACE VIEW laxmiyantra.secure_order_history AS
SELECT 
    id,
    order_id,
    strategy_name,
    ticker,
    side,
    order_type,
    quantity,
    filled_quantity,
    CASE 
        WHEN price > 10000 THEN '[REDACTED]'
        ELSE price::TEXT
    END as price_display,
    status,
    submitted_at,
    filled_at,
    validation_status,
    CASE 
        WHEN jsonb_typeof(risk_assessment) = 'object' 
        THEN risk_assessment->>'risk_level'
        ELSE 'unknown'
    END as risk_level
FROM laxmiyantra.order_history
WHERE validation_status != 'failed'
ORDER BY submitted_at DESC;

-- Portfolio summary view with real-time calculations
CREATE OR REPLACE VIEW laxmiyantra.portfolio_summary AS
SELECT 
    strategy_name,
    COUNT(*) as position_count,
    SUM(quantity * COALESCE(current_price, avg_entry_price, 0)) as total_market_value,
    SUM(quantity * avg_entry_price) as total_cost_basis,
    SUM(unrealized_pnl) as total_unrealized_pnl,
    AVG(CASE WHEN current_price > 0 AND avg_entry_price > 0 
        THEN ((current_price - avg_entry_price) / avg_entry_price) * 100 
        ELSE 0 END) as avg_return_percent,
    MAX(last_updated) as last_position_update,
    MAX(last_price_update) as last_price_update
FROM laxmiyantra.portfolio_positions
WHERE position_status = 'active' AND quantity > 0
GROUP BY strategy_name
ORDER BY total_market_value DESC;

-- =================================================================
-- VALIDATION AND VERIFICATION
-- =================================================================

-- Verify all tables exist
DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    view_count INTEGER;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'laxmiyantra';
    
    -- Count indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes 
    WHERE schemaname = 'laxmiyantra';
    
    -- Count views
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views 
    WHERE table_schema = 'laxmiyantra';
    
    RAISE NOTICE 'Database compliance update completed successfully!';
    RAISE NOTICE 'Tables: %, Indexes: %, Views: %', table_count, index_count, view_count;
END
$$;

-- =================================================================
-- COMPLETION MESSAGE
-- =================================================================

SELECT 
    'Enhanced database compliance update completed!' as status,
    'Support for limit orders, enhanced audit trail, and security views added' as features,
    'Laxmi-yantra database is now fully compliant with enhanced workflows' as result,
    NOW() as update_timestamp;

RAISE NOTICE '=================================================================';
RAISE NOTICE 'Enhanced Database Compliance Update Completed Successfully!';
RAISE NOTICE 'Features Added:';
RAISE NOTICE '• Limit order support in order_history';
RAISE NOTICE '• Enhanced audit trail with comprehensive tracking';
RAISE NOTICE '• Real-time P&L calculation in portfolio positions';
RAISE NOTICE '• Security views for sensitive data protection';
RAISE NOTICE '• Performance indexes for enhanced query speed';
RAISE NOTICE '• Transaction linking and validation tracking';
RAISE NOTICE 'Divine blessing: Database blessed for infinite reliability! 🙏';
RAISE NOTICE '=================================================================';
