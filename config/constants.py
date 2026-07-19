"""
Application constants and enums.
"""
from enum import Enum

class PipelineStatus(Enum):
    """Pipeline health status enumeration."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class SignOffStatus(Enum):
    """Sign-off status enumeration."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    PENDING = "PENDING"

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

class MetricType(Enum):
    """Types of metrics."""
    COMPLETENESS = "completeness"
    FRESHNESS = "freshness"
    RECONCILIATION = "reconciliation"
    QUALITY = "quality"
    PIPELINE_HEALTH = "pipeline_health"

# Validation rules
VALIDATION_RULES = {
    'completeness_min': 99.0,
    'freshness_min': 95.0,
    'reconciliation_match_min': 98.0,
    'null_threshold': 5.0,
    'duplicate_threshold': 2.0,
    'missing_records_threshold': 10
}

# Table definitions
SOURCE_TABLES = ['source_orders', 'source_customers', 'source_events']
WAREHOUSE_TABLES = ['warehouse_orders', 'warehouse_customers', 'warehouse_events']

# Primary keys for reconciliation
PRIMARY_KEYS = {
    'orders': 'order_id',
    'customers': 'customer_id',
    'events': 'event_id'
}

# Alert messages
ALERT_MESSAGES = {
    'completeness_low': "Completeness is below threshold",
    'freshness_stale': "Data is stale, freshness issue detected",
    'reconciliation_failed': "Reconciliation mismatch detected",
    'pipeline_failed': "Pipeline failure detected",
    'quality_degraded': "Quality score degraded"
}