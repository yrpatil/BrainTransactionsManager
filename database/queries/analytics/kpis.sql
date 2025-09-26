-- =================================================================
-- KPI Metrics Query (fast, production-grade)
-- - Portfolio MV proxy from last price * quantity where available
-- - Trade counts and volumes (last 30 days)
-- - Commission totals (last 30 days)
-- - Average execution latency (last 7 days)
-- =================================================================

SET search_path TO laxmiyantra, public;

WITH last_prices AS (
    SELECT DISTINCT ON (ticker)
        ticker,
        close AS last_price,
        timestamp AS last_price_time
    FROM ohlc_data
    WHERE timeframe = '1Min'
    ORDER BY ticker, timestamp DESC
),
positions AS (
    SELECT 
        strategy_name,
        ticker,
        quantity,
        avg_entry_price
    FROM portfolio_positions
),
position_values AS (
    SELECT 
        p.strategy_name,
        p.ticker,
        p.quantity,
        p.avg_entry_price,
        COALESCE(lp.last_price, p.avg_entry_price) AS mark_price,
        (p.quantity * COALESCE(lp.last_price, p.avg_entry_price)) AS market_value,
        CASE 
            WHEN p.avg_entry_price IS NOT NULL AND p.avg_entry_price > 0 THEN 
                ((COALESCE(lp.last_price, p.avg_entry_price) - p.avg_entry_price) / p.avg_entry_price) * 100.0
            ELSE NULL
        END AS unrealized_pnl_pct
    FROM positions p
    LEFT JOIN last_prices lp ON lp.ticker = p.ticker
),
trades_30d AS (
    SELECT 
        COUNT(*) AS trade_count_30d,
        SUM(CASE WHEN status = 'filled' THEN filled_quantity * filled_avg_price ELSE 0 END) AS volume_30d,
        SUM(commission) AS commission_30d
    FROM order_history
    WHERE submitted_at >= NOW() - INTERVAL '60 days'
),
latency_7d AS (
    SELECT 
        AVG(
            CASE 
                WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
                    EXTRACT(EPOCH FROM (filled_at - submitted_at))
                ELSE NULL
            END
        ) AS avg_exec_latency_7d
    FROM order_history
    WHERE submitted_at >= NOW() - INTERVAL '60 days'
),
agg AS (
    SELECT 
        SUM(market_value) AS portfolio_market_value,
        AVG(unrealized_pnl_pct) AS avg_position_unrealized_pnl_pct
    FROM position_values
)
SELECT 
    ROUND(agg.portfolio_market_value::numeric, 2) AS portfolio_market_value,
    ROUND(tr.trade_count_30d::numeric, 0) AS trade_count_30d,
    ROUND(tr.volume_30d::numeric, 2) AS traded_volume_30d,
    ROUND(tr.commission_30d::numeric, 4) AS commissions_30d,
    ROUND(lat.avg_exec_latency_7d::numeric, 2) AS avg_exec_latency_seconds_7d,
    ROUND(agg.avg_position_unrealized_pnl_pct::numeric, 4) AS avg_position_unrealized_pnl_pct
FROM agg
CROSS JOIN trades_30d tr
CROSS JOIN latency_7d lat;


