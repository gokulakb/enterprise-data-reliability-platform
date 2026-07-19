-- Source to Warehouse Reconciliation Queries

-- Overall Reconciliation Summary
SELECT 
    'Orders' as table_name,
    COUNT(DISTINCT source_orders.order_id) as source_count,
    COUNT(DISTINCT warehouse_orders.order_id) as warehouse_count,
    COUNT(DISTINCT source_orders.order_id) - COUNT(DISTINCT warehouse_orders.order_id) as missing_count,
    COUNT(DISTINCT warehouse_orders.order_id) - COUNT(DISTINCT source_orders.order_id) as extra_count,
    ROUND(COUNT(DISTINCT warehouse_orders.order_id) * 100.0 / NULLIF(COUNT(DISTINCT source_orders.order_id), 0), 2) as match_pct
FROM source_orders
LEFT JOIN warehouse_orders ON source_orders.order_id = warehouse_orders.order_id
UNION ALL
SELECT 
    'Customers' as table_name,
    COUNT(DISTINCT source_customers.customer_id) as source_count,
    COUNT(DISTINCT warehouse_customers.customer_id) as warehouse_count,
    COUNT(DISTINCT source_customers.customer_id) - COUNT(DISTINCT warehouse_customers.customer_id) as missing_count,
    COUNT(DISTINCT warehouse_customers.customer_id) - COUNT(DISTINCT source_customers.customer_id) as extra_count,
    ROUND(COUNT(DISTINCT warehouse_customers.customer_id) * 100.0 / NULLIF(COUNT(DISTINCT source_customers.customer_id), 0), 2) as match_pct
FROM source_customers
LEFT JOIN warehouse_customers ON source_customers.customer_id = warehouse_customers.customer_id
UNION ALL
SELECT 
    'Events' as table_name,
    COUNT(DISTINCT source_events.event_id) as source_count,
    COUNT(DISTINCT warehouse_events.event_id) as warehouse_count,
    COUNT(DISTINCT source_events.event_id) - COUNT(DISTINCT warehouse_events.event_id) as missing_count,
    COUNT(DISTINCT warehouse_events.event_id) - COUNT(DISTINCT source_events.event_id) as extra_count,
    ROUND(COUNT(DISTINCT warehouse_events.event_id) * 100.0 / NULLIF(COUNT(DISTINCT source_events.event_id), 0), 2) as match_pct
FROM source_events
LEFT JOIN warehouse_events ON source_events.event_id = warehouse_events.event_id;

-- Duplicate Records
SELECT 
    order_id as duplicate_key,
    COUNT(*) as duplicate_count
FROM warehouse_orders
GROUP BY order_id
HAVING COUNT(*) > 1;