-- Warehouse Data Validation Queries

-- 1. NULL Value Analysis
SELECT 
    'Orders' as table_name,
    COUNT(*) as total_records,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_order_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) as null_order_date,
    SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) as null_total_amount,
    SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) as null_status
FROM warehouse_orders
UNION ALL
SELECT 
    'Customers' as table_name,
    COUNT(*) as total_records,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
    SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) as null_name,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_email,
    0 as null_total_amount,
    0 as null_status
FROM warehouse_customers
UNION ALL
SELECT 
    'Events' as table_name,
    COUNT(*) as total_records,
    SUM(CASE WHEN event_id IS NULL THEN 1 ELSE 0 END) as null_event_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
    0 as null_order_date,
    0 as null_total_amount,
    0 as null_status
FROM warehouse_events;

-- 2. Schema Validation
SELECT 
    sql 
FROM sqlite_master 
WHERE type='table' 
AND name IN ('source_orders', 'warehouse_orders', 'source_customers', 
             'warehouse_customers', 'source_events', 'warehouse_events');

-- 3. Data Type Validation
SELECT 
    'Orders - Order ID' as validation,
    CASE 
        WHEN typeof(order_id) = 'integer' THEN 'PASS' 
        ELSE 'FAIL' 
    END as status
FROM warehouse_orders LIMIT 1
UNION ALL
SELECT 
    'Orders - Customer ID' as validation,
    CASE 
        WHEN typeof(customer_id) = 'integer' THEN 'PASS' 
        ELSE 'FAIL' 
    END as status
FROM warehouse_orders LIMIT 1
UNION ALL
SELECT 
    'Orders - Total Amount' as validation,
    CASE 
        WHEN typeof(total_amount) = 'real' OR typeof(total_amount) = 'integer' THEN 'PASS' 
        ELSE 'FAIL' 
    END as status
FROM warehouse_orders LIMIT 1;

-- 4. Timestamp Validation
SELECT 
    table_name,
    COUNT(*) as total_records,
    MIN(timestamp) as earliest_timestamp,
    MAX(timestamp) as latest_timestamp,
    ROUND((JULIANDAY(MAX(timestamp)) - JULIANDAY(MIN(timestamp))) * 24 * 60, 2) as timestamp_range_minutes
FROM (
    SELECT 'source_orders' as table_name, source_timestamp as timestamp FROM source_orders
    UNION ALL
    SELECT 'warehouse_orders' as table_name, warehouse_timestamp as timestamp FROM warehouse_orders
    UNION ALL
    SELECT 'source_customers' as table_name, source_timestamp as timestamp FROM source_customers
    UNION ALL
    SELECT 'warehouse_customers' as table_name, warehouse_timestamp as timestamp FROM warehouse_customers
    UNION ALL
    SELECT 'source_events' as table_name, source_timestamp as timestamp FROM source_events
    UNION ALL
    SELECT 'warehouse_events' as table_name, warehouse_timestamp as timestamp FROM warehouse_events
)
GROUP BY table_name;

-- 5. Referential Integrity Validation
SELECT 
    'Orders - Missing Customers' as validation,
    COUNT(*) as count
FROM warehouse_orders o
LEFT JOIN warehouse_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 
    'Events - Missing Customers' as validation,
    COUNT(*) as count
FROM warehouse_events e
LEFT JOIN warehouse_customers c ON e.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 6. Unique Constraint Validation
SELECT 
    'Orders - Unique Order ID' as validation,
    COUNT(*) as duplicates_count
FROM warehouse_orders
GROUP BY order_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 
    'Customers - Unique Customer ID' as validation,
    COUNT(*) as duplicates_count
FROM warehouse_customers
GROUP BY customer_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 
    'Events - Unique Event ID' as validation,
    COUNT(*) as duplicates_count
FROM warehouse_events
GROUP BY event_id
HAVING COUNT(*) > 1;

-- 7. Range Validation
SELECT 
    'Negative Amounts' as validation,
    COUNT(*) as count
FROM warehouse_orders
WHERE total_amount < 0
UNION ALL
SELECT 
    'Invalid Status' as validation,
    COUNT(*) as count
FROM warehouse_orders
WHERE status NOT IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

-- 8. Business Rule Validation
SELECT 
    'Pending Orders > 30 Days' as validation,
    COUNT(*) as count
FROM warehouse_orders
WHERE status = 'pending' 
AND JULIANDAY('now') - JULIANDAY(order_date) > 30
UNION ALL
SELECT 
    'Delivered Orders < 1 Day' as validation,
    COUNT(*) as count
FROM warehouse_orders
WHERE status = 'delivered' 
AND JULIANDAY('now') - JULIANDAY(order_date) < 1;