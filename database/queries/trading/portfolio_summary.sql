-- =================================================================
-- Portfolio Summary Query
-- Get current portfolio positions with performance metrics
-- =================================================================

SET search_path TO laxmiyantra, public;

SELECT 
    pp.strategy_name,
    pp.ticker,
    pp.quantity,
    pp.avg_entry_price,
    CASE 
        WHEN od.close IS NOT NULL THEN od.close
        ELSE pp.avg_entry_price 
    END as current_price,
    CASE 
        WHEN od.close IS NOT NULL AND pp.avg_entry_price > 0 THEN
            ROUND(((od.close - pp.avg_entry_price) / pp.avg_entry_price * 100)::numeric, 2)
        ELSE 0 
    END as unrealized_pnl_percent,
    CASE 
        WHEN od.close IS NOT NULL THEN
            ROUND((pp.quantity * (od.close - pp.avg_entry_price))::numeric, 2)
        ELSE 0 
    END as unrealized_pnl_amount,
    CASE 
        WHEN od.close IS NOT NULL THEN
            ROUND((pp.quantity * od.close)::numeric, 2)
        ELSE ROUND((pp.quantity * pp.avg_entry_price)::numeric, 2)
    END as market_value,
    pp.last_updated,
    pp.created_at
FROM portfolio_positions pp
LEFT JOIN LATERAL (
    SELECT close 
    FROM ohlc_data 
    WHERE ticker = pp.ticker 
    ORDER BY timestamp DESC 
    LIMIT 1
) od ON true
WHERE pp.quantity != 0
ORDER BY pp.strategy_name, pp.ticker;

-- Summary by strategy
SELECT 
    strategy_name,
    COUNT(*) as positions_count,
    SUM(CASE 
        WHEN od.close IS NOT NULL THEN
            ROUND((pp.quantity * od.close)::numeric, 2)
        ELSE ROUND((pp.quantity * pp.avg_entry_price)::numeric, 2)
    END) as total_market_value,
    SUM(CASE 
        WHEN od.close IS NOT NULL THEN
            ROUND((pp.quantity * (od.close - pp.avg_entry_price))::numeric, 2)
        ELSE 0 
    END) as total_unrealized_pnl
FROM portfolio_positions pp
LEFT JOIN LATERAL (
    SELECT close 
    FROM ohlc_data 
    WHERE ticker = pp.ticker 
    ORDER BY timestamp DESC 
    LIMIT 1
) od ON true
WHERE pp.quantity != 0
GROUP BY strategy_name
ORDER BY strategy_name;
