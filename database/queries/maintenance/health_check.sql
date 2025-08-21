-- =================================================================
-- Database Health Check Query
-- Comprehensive system health monitoring
-- =================================================================

SET search_path TO laxmiyantra, public;

-- Database connection and basic info
SELECT 
    'Database Health Check' as check_type,
    current_database() as database_name,
    current_schema() as current_schema,
    version() as postgresql_version,
    NOW() as check_timestamp;

-- Table sizes and row counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE schemaname = 'laxmiyantra'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'LOW_USAGE'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes 
WHERE schemaname = 'laxmiyantra'
ORDER BY idx_scan DESC;

-- TimescaleDB hypertable status
SELECT 
    ht.schema_name,
    ht.table_name,
    ht.num_dimensions,
    d.column_name as time_column,
    d.interval_length,
    pg_size_pretty(hypertable_size(format('%I.%I', ht.schema_name, ht.table_name))) as hypertable_size
FROM _timescaledb_catalog.hypertable ht
JOIN _timescaledb_catalog.dimension d ON ht.id = d.hypertable_id
WHERE ht.schema_name = 'laxmiyantra';

-- Recent chunk information for OHLC data
SELECT 
    chunk_schema,
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(pg_total_relation_size(chunk_schema||'.'||chunk_name)) as chunk_size,
    (SELECT COUNT(*) FROM pg_stat_user_tables WHERE schemaname = chunk_schema AND tablename = chunk_name) as row_count_available
FROM chunk_relation_size('laxmiyantra.ohlc_data')
ORDER BY range_start DESC
LIMIT 10;

-- Active connections and queries
SELECT 
    datname,
    usename,
    client_addr,
    state,
    NOW() - query_start as query_duration,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity 
WHERE datname = current_database()
    AND state != 'idle'
ORDER BY query_start;

-- Lock analysis
SELECT 
    l.locktype,
    l.database,
    l.relation::regclass as table_name,
    l.mode,
    l.granted,
    a.usename,
    a.client_addr,
    NOW() - a.query_start as duration,
    LEFT(a.query, 100) as query_preview
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY a.query_start;

-- Recent transaction log analysis
SELECT 
    module_name,
    transaction_type,
    status,
    COUNT(*) as count,
    AVG(execution_time_seconds) as avg_execution_time,
    MAX(execution_time_seconds) as max_execution_time,
    MIN(created_at) as earliest_transaction,
    MAX(created_at) as latest_transaction
FROM transaction_log
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY module_name, transaction_type, status
ORDER BY count DESC;

-- Error analysis from transaction log
SELECT 
    module_name,
    error_message,
    COUNT(*) as error_count,
    MAX(created_at) as last_occurrence
FROM transaction_log
WHERE error_message IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY module_name, error_message
ORDER BY error_count DESC, last_occurrence DESC;

-- System status check
SELECT 
    component_name,
    is_active,
    status_message,
    last_heartbeat,
    NOW() - last_heartbeat as time_since_heartbeat,
    CASE 
        WHEN NOW() - last_heartbeat > INTERVAL '5 minutes' THEN 'STALE'
        WHEN is_active = false THEN 'INACTIVE'
        ELSE 'HEALTHY'
    END as health_status
FROM system_status
ORDER BY component_name;

-- Database settings check
SELECT 
    name,
    setting,
    unit,
    short_desc
FROM pg_settings 
WHERE name IN (
    'shared_buffers',
    'effective_cache_size', 
    'maintenance_work_mem',
    'work_mem',
    'max_connections',
    'checkpoint_completion_target',
    'wal_buffers'
)
ORDER BY name;
