-- =================================================================
-- Strategy Performance (30d window)
-- - Volume, commissions, execution latency
-- - Active tickers, trade counts
-- - Supports optional filtering by strategy via placeholder
-- =================================================================

-- Usage hint (client should replace :strategy_name or remove WHERE clause):
-- WHERE (:strategy_name IS NULL OR strategy_name = :strategy_name)

SET search_path TO laxmiyantra, public;

WITH base AS (
    SELECT 
        strategy_name,
        ticker,
        status,
        submitted_at,
        filled_at,
        commission,
        CASE WHEN status = 'filled' THEN filled_quantity * filled_avg_price ELSE 0 END AS traded_value
    FROM order_history
    WHERE submitted_at >= NOW() - INTERVAL '60 days'
),
stats AS (
    SELECT 
        strategy_name,
        COUNT(*) AS total_trades,
        SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) AS filled_trades,
        SUM(traded_value) AS total_volume,
        SUM(commission) AS total_commission,
        COUNT(DISTINCT ticker) AS unique_tickers,
        AVG(
            CASE 
                WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
                    EXTRACT(EPOCH FROM (filled_at - submitted_at))
                ELSE NULL
            END
        ) AS avg_execution_time,
        MIN(submitted_at) AS first_trade,
        MAX(submitted_at) AS last_trade
    FROM base
    GROUP BY strategy_name
)
SELECT 
    strategy_name,
    total_trades,
    filled_trades,
    ROUND((filled_trades::numeric / NULLIF(total_trades, 0) * 100), 2) AS fill_rate_percent,
    ROUND(total_volume::numeric, 2) AS total_volume,
    ROUND(total_commission::numeric, 4) AS total_commission,
    unique_tickers,
    ROUND(avg_execution_time::numeric, 2) AS avg_execution_time_seconds,
    first_trade,
    last_trade,
    EXTRACT(DAYS FROM (last_trade - first_trade)) AS active_days
FROM stats
ORDER BY total_volume DESC;


