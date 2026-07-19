-- Pipeline Health Queries

-- Overall Pipeline Status
SELECT 
    pipeline_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
    ROUND(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM pipeline_runs
WHERE start_time >= datetime('now', '-1 day')
GROUP BY pipeline_name;

-- Pipeline Run Details
SELECT 
    run_id,
    pipeline_name,
    start_time,
    end_time,
    status,
    records_processed,
    error_message
FROM pipeline_runs
WHERE start_time >= datetime('now', '-1 day')
ORDER BY start_time DESC
LIMIT 20;

-- Pipeline Health Summary
SELECT 
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
    ROUND(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate,
    AVG(strftime('%s', end_time) - strftime('%s', start_time)) as avg_duration_seconds
FROM pipeline_runs
WHERE start_time >= datetime('now', '-1 day');