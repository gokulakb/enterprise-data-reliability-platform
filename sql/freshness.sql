-- Data Freshness Validation Queries

-- Overall Freshness
SELECT 
    MAX(source_timestamp) as latest_source,
    MAX(warehouse_timestamp) as latest_warehouse,
    strftime('%s', MAX(warehouse_timestamp)) - strftime('%s', MAX(source_timestamp)) as delay_seconds,
    ROUND((strftime('%s', MAX(warehouse_timestamp)) - strftime('%s', MAX(source_timestamp))) / 60.0, 2) as delay_minutes
FROM (
    SELECT source_timestamp, warehouse_timestamp 
    FROM source_orders 
    JOIN warehouse_orders ON source_orders.order_id = warehouse_orders.order_id
);

-- Freshness by Table
SELECT 
    'Orders' as table_name,
    (SELECT MAX(source_timestamp) FROM source_orders) as latest_source,
    (SELECT MAX(warehouse_timestamp) FROM warehouse_orders) as latest_warehouse,
    ROUND((strftime('%s', (SELECT MAX(warehouse_timestamp) FROM warehouse_orders)) - 
           strftime('%s', (SELECT MAX(source_timestamp) FROM source_orders))) / 60.0, 2) as delay_minutes
UNION ALL
SELECT 
    'Customers' as table_name,
    (SELECT MAX(source_timestamp) FROM source_customers) as latest_source,
    (SELECT MAX(warehouse_timestamp) FROM warehouse_customers) as latest_warehouse,
    ROUND((strftime('%s', (SELECT MAX(warehouse_timestamp) FROM warehouse_customers)) - 
           strftime('%s', (SELECT MAX(source_timestamp) FROM source_customers))) / 60.0, 2) as delay_minutes
UNION ALL
SELECT 
    'Events' as table_name,
    (SELECT MAX(source_timestamp) FROM source_events) as latest_source,
    (SELECT MAX(warehouse_timestamp) FROM warehouse_events) as latest_warehouse,
    ROUND((strftime('%s', (SELECT MAX(warehouse_timestamp) FROM warehouse_events)) - 
           strftime('%s', (SELECT MAX(source_timestamp) FROM source_events))) / 60.0, 2) as delay_minutes;