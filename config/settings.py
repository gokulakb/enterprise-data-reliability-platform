"""
Application configuration settings.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
EXPORTS_DIR = BASE_DIR / 'exports'
REPORTS_DIR = BASE_DIR / 'reports'
ASSETS_DIR = BASE_DIR / 'assets'
SQL_DIR = BASE_DIR / 'sql'

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, EXPORTS_DIR, REPORTS_DIR, ASSETS_DIR, SQL_DIR]:
    dir_path.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = f"sqlite:///{BASE_DIR}/enterprise_reliability.db"

# Application settings
APP_NAME = "Enterprise Data Reliability Platform"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Enterprise-grade data reliability monitoring and validation platform"

# Thresholds for reliability scoring
THRESHOLDS = {
    'reliability_pass': 98,
    'reliability_warning_min': 90,
    'freshness_pass': 95,
    'completeness_pass': 99,
    'reconciliation_pass': 98,
    'critical_alert_threshold': 5,
    'warning_alert_threshold': 10
}

# Pipeline status thresholds
PIPELINE_STATUS = {
    'success_rate_pass': 95,
    'critical_delay_minutes': 60,
    'warning_delay_minutes': 30
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'application.log'
}

# Export formats
EXPORT_FORMATS = ['csv', 'excel', 'pdf']

# Date formats
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Table configurations
TABLES = {
    'orders': {
        'source': 'source_orders',
        'warehouse': 'warehouse_orders',
        'primary_key': 'order_id',
        'timestamp_columns': ['order_date', 'source_timestamp', 'warehouse_timestamp']
    },
    'customers': {
        'source': 'source_customers',
        'warehouse': 'warehouse_customers',
        'primary_key': 'customer_id',
        'timestamp_columns': ['created_at', 'source_timestamp', 'warehouse_timestamp']
    },
    'events': {
        'source': 'source_events',
        'warehouse': 'warehouse_events',
        'primary_key': 'event_id',
        'timestamp_columns': ['event_timestamp', 'source_timestamp', 'warehouse_timestamp']
    }
}

# Metric weights for quality score
QUALITY_WEIGHTS = {
    'completeness': 0.30,
    'freshness': 0.25,
    'reconciliation': 0.25,
    'pipeline_health': 0.20
}