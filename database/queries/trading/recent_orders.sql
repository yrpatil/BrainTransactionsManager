-- =================================================================
-- Recent Orders Query
-- View recent order activity with status and performance
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Recent orders (last 24 hours)
SELECT 
    oh.order_id,
    oh.strategy_name,
    oh.ticker,
    oh.side,
    oh.order_type,
    oh.quantity,
    oh.filled_quantity,
    oh.price,
    oh.filled_avg_price,
    oh.status,
    oh.commission,
    oh.submitted_at,
    oh.filled_at,
    CASE 
        WHEN oh.filled_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (oh.filled_at - oh.submitted_at))
        ELSE NULL
    END as fill_time_seconds,
    oh.notes
FROM order_history oh
WHERE oh.submitted_at >= NOW() - INTERVAL '24 hours'
ORDER BY oh.submitted_at DESC
LIMIT 50;

-- Order status summary (last 7 days)
SELECT 
    status,
    COUNT(*) as order_count,
    SUM(quantity) as total_quantity,
    SUM(filled_quantity) as total_filled_quantity,
    ROUND(AVG(CASE 
        WHEN filled_at IS NOT NULL AND submitted_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (filled_at - submitted_at))
        ELSE NULL
    END)::numeric, 2) as avg_fill_time_seconds
FROM order_history
WHERE submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY status
ORDER BY order_count DESC;

-- Orders by strategy (last 7 days)
SELECT 
    strategy_name,
    COUNT(*) as total_orders,
    SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as filled_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_orders,
    ROUND((SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100), 2) as fill_rate_percent,
    SUM(filled_quantity * COALESCE(filled_avg_price, price, 0)) as total_volume
FROM order_history
WHERE submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY strategy_name
ORDER BY total_orders DESC;
