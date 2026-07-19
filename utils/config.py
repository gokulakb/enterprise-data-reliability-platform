# utils/config.py
"""
Configuration management.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
EXPORTS_DIR = BASE_DIR / 'exports'
REPORTS_DIR = BASE_DIR / 'reports'
SQL_DIR = BASE_DIR / 'sql'
ASSETS_DIR = BASE_DIR / 'assets'

# Create directories
for dir_path in [DATA_DIR, LOGS_DIR, EXPORTS_DIR, REPORTS_DIR, SQL_DIR, ASSETS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR}/enterprise_reliability.db")

# Application settings
APP_NAME = "Enterprise Data Reliability Platform"
APP_VERSION = "1.0.0"
APP_ENV = os.getenv('APP_ENV', 'development')
DEBUG = APP_ENV == 'development'

# Thresholds
THRESHOLDS = {
    'reliability_pass': 98.0,
    'reliability_warning': 90.0,
    'freshness_pass': 95.0,
    'completeness_pass': 99.0,
    'reconciliation_pass': 98.0,
    'quality_pass': 95.0,
}

# Alert thresholds
ALERT_THRESHOLDS = {
    'critical': {
        'completeness': 90.0,
        'freshness': 80.0,
        'reconciliation': 90.0,
        'pipeline_success': 80.0,
    },
    'warning': {
        'completeness': 95.0,
        'freshness': 90.0,
        'reconciliation': 95.0,
        'pipeline_success': 90.0,
    }
}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = LOGS_DIR / 'application.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Export settings
EXPORT_FORMATS = ['csv', 'excel', 'pdf']
MAX_EXPORT_ROWS = 10000

# Pipeline settings
PIPELINE_SETTINGS = {
    'max_delay_minutes': 60,
    'warning_delay_minutes': 30,
    'success_rate_threshold': 95.0,
    'max_failures': 3,
}

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
    'pipeline_health': 0.20,
}

def get_config():
    """Get application configuration."""
    return {
        'app_name': APP_NAME,
        'app_version': APP_VERSION,
        'app_env': APP_ENV,
        'debug': DEBUG,
        'database_url': DATABASE_URL,
        'thresholds': THRESHOLDS,
        'alert_thresholds': ALERT_THRESHOLDS,
        'quality_weights': QUALITY_WEIGHTS,
        'tables': TABLES,
        'pipeline_settings': PIPELINE_SETTINGS,
    }