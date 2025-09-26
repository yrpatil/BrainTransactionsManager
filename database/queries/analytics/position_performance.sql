-- =================================================================
-- Position Performance Table Query
-- Show current holdings with P&L, cost basis, and performance metrics
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Get current positions with latest prices and P&L
WITH current_positions AS (
    SELECT 
        strategy_name,
        ticker,
        quantity,
        avg_entry_price,
        last_updated
    FROM portfolio_positions
    WHERE quantity != 0  -- Only active positions
),

-- Get latest price for each ticker
latest_prices AS (
    SELECT DISTINCT ON (ticker)
        ticker,
        close as current_price,
        timestamp as price_timestamp
    FROM ohlc_data
    WHERE timeframe = '1Min'
    ORDER BY ticker, timestamp DESC
),

-- Calculate position performance
position_performance AS (
    SELECT 
        cp.strategy_name,
        cp.ticker,
        cp.quantity,
        cp.avg_entry_price,
        COALESCE(lp.current_price, cp.avg_entry_price) as current_price,
        lp.price_timestamp,
        -- Market value calculations
        (cp.quantity * cp.avg_entry_price) as cost_basis,
        (cp.quantity * COALESCE(lp.current_price, cp.avg_entry_price)) as market_value,
        -- P&L calculations
        (cp.quantity * (COALESCE(lp.current_price, cp.avg_entry_price) - cp.avg_entry_price)) as unrealized_pnl,
        -- Percentage calculations
        CASE 
            WHEN cp.avg_entry_price > 0 THEN 
                ((COALESCE(lp.current_price, cp.avg_entry_price) - cp.avg_entry_price) / cp.avg_entry_price) * 100
            ELSE 0 
        END as pnl_percent,
        -- Position age
        EXTRACT(DAYS FROM (NOW() - cp.last_updated)) as days_held
    FROM current_positions cp
    LEFT JOIN latest_prices lp ON lp.ticker = cp.ticker
)

-- Return position performance for table display
SELECT 
    strategy_name,
    ticker,
    quantity,
    ROUND(avg_entry_price::numeric, 2) as entry_price,
    ROUND(current_price::numeric, 2) as current_price,
    ROUND(cost_basis::numeric, 2) as cost_basis,
    ROUND(market_value::numeric, 2) as market_value,
    ROUND(unrealized_pnl::numeric, 2) as unrealized_pnl,
    ROUND(pnl_percent::numeric, 2) as pnl_percent,
    days_held::integer as days_held,
    price_timestamp as last_price_update
FROM position_performance
ORDER BY ABS(unrealized_pnl) DESC;  -- Show biggest gains/losses first
