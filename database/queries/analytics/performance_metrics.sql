-- =================================================================
-- Performance Metrics Query
-- Comprehensive trading performance analysis
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Daily performance summary
WITH daily_trades AS (
    SELECT 
        DATE(submitted_at) as trade_date,
        strategy_name,
        ticker,
        side,
        filled_quantity,
        filled_avg_price,
        commission
    FROM order_history
    WHERE status = 'filled'
        AND submitted_at >= NOW() - INTERVAL '30 days'
),
daily_volume AS (
    SELECT 
        trade_date,
        strategy_name,
        COUNT(*) as trades_count,
        SUM(filled_quantity * filled_avg_price) as total_volume,
        SUM(commission) as total_commission,
        COUNT(DISTINCT ticker) as unique_tickers
    FROM daily_trades
    GROUP BY trade_date, strategy_name
)
SELECT 
    trade_date,
    strategy_name,
    trades_count,
    ROUND(total_volume::numeric, 2) as total_volume,
    ROUND(total_commission::numeric, 4) as total_commission,
    unique_tickers,
    ROUND((total_volume / NULLIF(trades_count, 0))::numeric, 2) as avg_trade_size
FROM daily_volume
ORDER BY trade_date DESC, strategy_name;

-- Strategy performance comparison
WITH strategy_stats AS (
    SELECT 
        strategy_name,
        COUNT(*) as total_trades,
        SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as successful_trades,
        SUM(CASE WHEN status = 'filled' THEN filled_quantity * filled_avg_price ELSE 0 END) as total_volume,
        SUM(commission) as total_commission,
        AVG(CASE 
            WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
                EXTRACT(EPOCH FROM (filled_at - submitted_at))
            ELSE NULL
        END) as avg_execution_time,
        MIN(submitted_at) as first_trade,
        MAX(submitted_at) as last_trade,
        COUNT(DISTINCT ticker) as unique_tickers
    FROM order_history
    WHERE submitted_at >= NOW() - INTERVAL '30 days'
    GROUP BY strategy_name
)
SELECT 
    strategy_name,
    total_trades,
    successful_trades,
    ROUND((successful_trades::numeric / NULLIF(total_trades, 0) * 100), 2) as success_rate_percent,
    ROUND(total_volume::numeric, 2) as total_volume,
    ROUND(total_commission::numeric, 4) as total_commission,
    ROUND(avg_execution_time::numeric, 2) as avg_execution_time_seconds,
    unique_tickers,
    first_trade,
    last_trade,
    EXTRACT(DAYS FROM (last_trade - first_trade)) as active_days
FROM strategy_stats
ORDER BY total_volume DESC;

-- Top performing tickers
SELECT 
    ticker,
    COUNT(*) as trade_count,
    SUM(CASE WHEN status = 'filled' THEN filled_quantity * filled_avg_price ELSE 0 END) as total_volume,
    AVG(CASE 
        WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (filled_at - submitted_at))
        ELSE NULL
    END) as avg_execution_time,
    COUNT(DISTINCT strategy_name) as strategies_count,
    MAX(submitted_at) as last_trade_time
FROM order_history
WHERE submitted_at >= NOW() - INTERVAL '30 days'
GROUP BY ticker
HAVING COUNT(*) >= 5  -- Only tickers with at least 5 trades
ORDER BY total_volume DESC
LIMIT 20;

-- Hourly trading pattern
SELECT 
    EXTRACT(HOUR FROM submitted_at) as hour_of_day,
    COUNT(*) as trade_count,
    SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as successful_trades,
    ROUND(AVG(CASE 
        WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (filled_at - submitted_at))
        ELSE NULL
    END)::numeric, 2) as avg_execution_time
FROM order_history
WHERE submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY EXTRACT(HOUR FROM submitted_at)
ORDER BY hour_of_day;
