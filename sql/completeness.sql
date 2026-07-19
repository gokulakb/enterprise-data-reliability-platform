-- Data Completeness Validation Queries

-- Overall Completeness
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN is_complete = 1 THEN 1 ELSE 0 END) as complete_records,
    ROUND(SUM(CASE WHEN is_complete = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completeness_pct
FROM warehouse_orders;

-- Completeness by Table
SELECT 
    'Orders' as table_name,
    (SELECT COUNT(*) FROM source_orders) as source_count,
    (SELECT COUNT(*) FROM warehouse_orders) as warehouse_count,
    ROUND((SELECT COUNT(*) FROM warehouse_orders) * 100.0 / NULLIF((SELECT COUNT(*) FROM source_orders), 0), 2) as completeness_pct
UNION ALL
SELECT 
    'Customers' as table_name,
    (SELECT COUNT(*) FROM source_customers) as source_count,
    (SELECT COUNT(*) FROM warehouse_customers) as warehouse_count,
    ROUND((SELECT COUNT(*) FROM warehouse_customers) * 100.0 / NULLIF((SELECT COUNT(*) FROM source_customers), 0), 2) as completeness_pct
UNION ALL
SELECT 
    'Events' as table_name,
    (SELECT COUNT(*) FROM source_events) as source_count,
    (SELECT COUNT(*) FROM warehouse_events) as warehouse_count,
    ROUND((SELECT COUNT(*) FROM warehouse_events) * 100.0 / NULLIF((SELECT COUNT(*) FROM source_events), 0), 2) as completeness_pct;

-- Missing Records
SELECT 
    'Orders' as table_name,
    (SELECT COUNT(*) FROM source_orders) - (SELECT COUNT(*) FROM warehouse_orders) as missing_records
UNION ALL
SELECT 
    'Customers' as table_name,
    (SELECT COUNT(*) FROM source_customers) - (SELECT COUNT(*) FROM warehouse_customers) as missing_records
UNION ALL
SELECT 
    'Events' as table_name,
    (SELECT COUNT(*) FROM source_events) - (SELECT COUNT(*) FROM warehouse_events) as missing_records;