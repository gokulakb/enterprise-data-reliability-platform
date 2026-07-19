-- Dashboard Queries

-- Overall Data Quality Score
WITH metrics AS (
    SELECT 
        (SELECT ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM source_orders), 0), 2) 
         FROM warehouse_orders) as completeness,
        (SELECT ROUND(
            CASE 
                WHEN AVG(delay_hours) <= 1 THEN 100
                WHEN AVG(delay_hours) <= 4 THEN 95
                WHEN AVG(delay_hours) <= 8 THEN 85
                ELSE 70
            END, 2)
         FROM (
             SELECT (strftime('%s', warehouse_timestamp) - strftime('%s', source_timestamp)) / 3600.0 as delay_hours
             FROM source_orders
             JOIN warehouse_orders ON source_orders.order_id = warehouse_orders.order_id
         )) as freshness,
        (SELECT ROUND(COUNT(DISTINCT warehouse_orders.order_id) * 100.0 / NULLIF(COUNT(DISTINCT source_orders.order_id), 0), 2)
         FROM source_orders
         LEFT JOIN warehouse_orders ON source_orders.order_id = warehouse_orders.order_id) as reconciliation,
        (SELECT ROUND(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
         FROM pipeline_runs
         WHERE start_time >= datetime('now', '-1 day')) as pipeline_health
)
SELECT 
    ROUND(completeness * 0.30 + freshness * 0.25 + reconciliation * 0.25 + pipeline_health * 0.20, 2) as quality_score,
    completeness,
    freshness,
    reconciliation,
    pipeline_health
FROM metrics;

-- Recent Audit Logs
SELECT 
    timestamp,
    user,
    action,
    metric_type,
    metric_value,
    status,
    details
FROM audit_logs
ORDER BY timestamp DESC
LIMIT 20;

-- Alert Summary
SELECT 
    type,
    severity,
    COUNT(*) as count,
    MAX(timestamp) as last_occurrence
FROM alerts
WHERE timestamp >= datetime('now', '-1 day')
GROUP BY type, severity
ORDER BY severity DESC, count DESC;