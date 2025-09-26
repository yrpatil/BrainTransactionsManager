-- =================================================================
-- Daily P&L Performance Query
-- Calculate daily profit/loss based on current holdings and market prices
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Get current portfolio positions
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

-- Get recent price data for each ticker (last 30 days)
recent_prices AS (
    SELECT DISTINCT ON (ticker, DATE(timestamp))
        ticker,
        DATE(timestamp) as price_date,
        close as closing_price,
        timestamp
    FROM ohlc_data
    WHERE timeframe = '1Min'
        AND timestamp >= NOW() - INTERVAL '30 days'
    ORDER BY ticker, DATE(timestamp), timestamp DESC
),

-- Calculate daily P&L for each position
daily_position_pnl AS (
    SELECT 
        cp.strategy_name,
        cp.ticker,
        cp.quantity,
        cp.avg_entry_price,
        rp.price_date,
        rp.closing_price,
        -- Calculate unrealized P&L for this position on this date
        (cp.quantity * (rp.closing_price - cp.avg_entry_price)) as daily_unrealized_pnl,
        -- Calculate position market value
        (cp.quantity * rp.closing_price) as position_market_value,
        -- Calculate cost basis
        (cp.quantity * cp.avg_entry_price) as position_cost_basis
    FROM current_positions cp
    INNER JOIN recent_prices rp ON rp.ticker = cp.ticker
),

-- Aggregate daily P&L by date and strategy
daily_strategy_pnl AS (
    SELECT 
        price_date,
        strategy_name,
        COUNT(*) as positions_count,
        SUM(daily_unrealized_pnl) as daily_pnl,
        SUM(position_market_value) as total_market_value,
        SUM(position_cost_basis) as total_cost_basis,
        CASE 
            WHEN SUM(position_cost_basis) > 0 THEN 
                (SUM(daily_unrealized_pnl) / SUM(position_cost_basis)) * 100
            ELSE 0 
        END as daily_pnl_percent
    FROM daily_position_pnl
    GROUP BY price_date, strategy_name
),

-- Total portfolio daily P&L
daily_portfolio_pnl AS (
    SELECT 
        price_date,
        SUM(daily_pnl) as total_daily_pnl,
        SUM(total_market_value) as total_portfolio_value,
        SUM(total_cost_basis) as total_cost_basis,
        CASE 
            WHEN SUM(total_cost_basis) > 0 THEN 
                (SUM(daily_pnl) / SUM(total_cost_basis)) * 100
            ELSE 0 
        END as portfolio_pnl_percent,
        COUNT(DISTINCT strategy_name) as active_strategies
    FROM daily_strategy_pnl
    GROUP BY price_date
)

-- Return daily portfolio P&L for charting
SELECT 
    price_date,
    ROUND(total_daily_pnl::numeric, 2) as daily_pnl,
    ROUND(total_portfolio_value::numeric, 2) as portfolio_value,
    ROUND(total_cost_basis::numeric, 2) as cost_basis,
    ROUND(portfolio_pnl_percent::numeric, 2) as pnl_percent,
    active_strategies
FROM daily_portfolio_pnl
ORDER BY price_date DESC
LIMIT 30;
