-- =================================================================
-- Calculate Portfolio PnL Function
-- Calculate realized and unrealized P&L for portfolios
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Function to calculate portfolio PnL
CREATE OR REPLACE FUNCTION calculate_portfolio_pnl(
    p_strategy_name VARCHAR(255) DEFAULT NULL,
    p_ticker VARCHAR(50) DEFAULT NULL,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    strategy_name VARCHAR(255),
    ticker VARCHAR(50),
    current_quantity DECIMAL(20, 8),
    avg_entry_price DECIMAL(20, 8),
    current_price DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    unrealized_pnl_percent DECIMAL(10, 4),
    realized_pnl DECIMAL(20, 8),
    total_pnl DECIMAL(20, 8),
    market_value DECIMAL(20, 8),
    total_invested DECIMAL(20, 8),
    last_updated TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
DECLARE
    default_start_date DATE := CURRENT_DATE - INTERVAL '1 year';
    default_end_date DATE := CURRENT_DATE;
BEGIN
    -- Set default dates if not provided
    IF p_start_date IS NULL THEN
        p_start_date := default_start_date;
    END IF;
    
    IF p_end_date IS NULL THEN
        p_end_date := default_end_date;
    END IF;
    
    RETURN QUERY
    WITH portfolio_positions AS (
        SELECT 
            pp.strategy_name,
            pp.ticker,
            pp.quantity as current_quantity,
            pp.avg_entry_price,
            pp.last_updated
        FROM laxmiyantra.portfolio_positions pp
        WHERE pp.quantity != 0
            AND (p_strategy_name IS NULL OR pp.strategy_name = p_strategy_name)
            AND (p_ticker IS NULL OR pp.ticker = p_ticker)
    ),
    current_prices AS (
        SELECT DISTINCT ON (ticker)
            ticker,
            close as current_price
        FROM laxmiyantra.ohlc_data
        WHERE timestamp >= p_start_date AND timestamp <= p_end_date + INTERVAL '1 day'
        ORDER BY ticker, timestamp DESC
    ),
    realized_pnl_calc AS (
        SELECT 
            oh.strategy_name,
            oh.ticker,
            -- Calculate realized PnL from completed buy/sell pairs
            SUM(CASE 
                WHEN oh.side = 'sell' THEN 
                    oh.filled_quantity * oh.filled_avg_price
                WHEN oh.side = 'buy' THEN 
                    -oh.filled_quantity * oh.filled_avg_price
                ELSE 0
            END) - SUM(COALESCE(oh.commission, 0)) as realized_pnl
        FROM laxmiyantra.order_history oh
        WHERE oh.status = 'filled'
            AND oh.submitted_at >= p_start_date 
            AND oh.submitted_at <= p_end_date + INTERVAL '1 day'
            AND (p_strategy_name IS NULL OR oh.strategy_name = p_strategy_name)
            AND (p_ticker IS NULL OR oh.ticker = p_ticker)
        GROUP BY oh.strategy_name, oh.ticker
    )
    SELECT 
        pp.strategy_name,
        pp.ticker,
        pp.current_quantity,
        pp.avg_entry_price,
        COALESCE(cp.current_price, pp.avg_entry_price) as current_price,
        -- Unrealized PnL
        CASE 
            WHEN cp.current_price IS NOT NULL AND pp.avg_entry_price > 0 THEN
                pp.current_quantity * (cp.current_price - pp.avg_entry_price)
            ELSE 0
        END as unrealized_pnl,
        -- Unrealized PnL percentage
        CASE 
            WHEN cp.current_price IS NOT NULL AND pp.avg_entry_price > 0 THEN
                ((cp.current_price - pp.avg_entry_price) / pp.avg_entry_price * 100)
            ELSE 0
        END as unrealized_pnl_percent,
        -- Realized PnL
        COALESCE(rp.realized_pnl, 0) as realized_pnl,
        -- Total PnL
        CASE 
            WHEN cp.current_price IS NOT NULL AND pp.avg_entry_price > 0 THEN
                pp.current_quantity * (cp.current_price - pp.avg_entry_price) + COALESCE(rp.realized_pnl, 0)
            ELSE COALESCE(rp.realized_pnl, 0)
        END as total_pnl,
        -- Market value
        CASE 
            WHEN cp.current_price IS NOT NULL THEN
                pp.current_quantity * cp.current_price
            ELSE pp.current_quantity * pp.avg_entry_price
        END as market_value,
        -- Total invested
        pp.current_quantity * pp.avg_entry_price as total_invested,
        pp.last_updated
    FROM portfolio_positions pp
    LEFT JOIN current_prices cp ON pp.ticker = cp.ticker
    LEFT JOIN realized_pnl_calc rp ON pp.strategy_name = rp.strategy_name AND pp.ticker = rp.ticker
    ORDER BY pp.strategy_name, pp.ticker;
END;
$$;

-- Function to get portfolio summary by strategy
CREATE OR REPLACE FUNCTION get_portfolio_summary_by_strategy(
    p_strategy_name VARCHAR(255) DEFAULT NULL
)
RETURNS TABLE (
    strategy_name VARCHAR(255),
    total_positions INTEGER,
    total_market_value DECIMAL(20, 8),
    total_invested DECIMAL(20, 8),
    total_unrealized_pnl DECIMAL(20, 8),
    total_realized_pnl DECIMAL(20, 8),
    total_pnl DECIMAL(20, 8),
    total_pnl_percent DECIMAL(10, 4),
    best_performer VARCHAR(50),
    worst_performer VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH pnl_data AS (
        SELECT * FROM calculate_portfolio_pnl(p_strategy_name, NULL, NULL, NULL)
    ),
    strategy_summary AS (
        SELECT 
            pd.strategy_name,
            COUNT(*)::INTEGER as total_positions,
            SUM(pd.market_value) as total_market_value,
            SUM(pd.total_invested) as total_invested,
            SUM(pd.unrealized_pnl) as total_unrealized_pnl,
            SUM(pd.realized_pnl) as total_realized_pnl,
            SUM(pd.total_pnl) as total_pnl
        FROM pnl_data pd
        GROUP BY pd.strategy_name
    ),
    best_worst AS (
        SELECT 
            pd.strategy_name,
            (SELECT ticker FROM pnl_data WHERE strategy_name = pd.strategy_name ORDER BY unrealized_pnl_percent DESC LIMIT 1) as best_performer,
            (SELECT ticker FROM pnl_data WHERE strategy_name = pd.strategy_name ORDER BY unrealized_pnl_percent ASC LIMIT 1) as worst_performer
        FROM pnl_data pd
        GROUP BY pd.strategy_name
    )
    SELECT 
        ss.strategy_name,
        ss.total_positions,
        ss.total_market_value,
        ss.total_invested,
        ss.total_unrealized_pnl,
        ss.total_realized_pnl,
        ss.total_pnl,
        CASE 
            WHEN ss.total_invested > 0 THEN (ss.total_pnl / ss.total_invested * 100)
            ELSE 0
        END as total_pnl_percent,
        bw.best_performer,
        bw.worst_performer
    FROM strategy_summary ss
    LEFT JOIN best_worst bw ON ss.strategy_name = bw.strategy_name
    ORDER BY ss.total_pnl DESC;
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION calculate_portfolio_pnl TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_portfolio_summary_by_strategy TO PUBLIC;
