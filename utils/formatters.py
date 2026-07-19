"""
Data formatting utilities.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

from config.settings import DATE_FORMAT, DATETIME_FORMAT

def format_date(date_obj: datetime) -> str:
    """Format datetime object to date string."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime(DATE_FORMAT)
    return str(date_obj)

def format_datetime(dt_obj: datetime) -> str:
    """Format datetime object to datetime string."""
    if isinstance(dt_obj, datetime):
        return dt_obj.strftime(DATETIME_FORMAT)
    return str(dt_obj)

def format_metric_card(value: Any, decimals: int = 1) -> str:
    """Format metric value for display in cards."""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)

def format_status_badge(status: str) -> str:
    """Format status for badge display."""
    status_colors = {
        'PASS': '🟢',
        'WARNING': '🟡',
        'FAIL': '🔴',
        'HEALTHY': '🟢',
        'CRITICAL': '🔴',
        'PENDING': '🔵',
        'UNKNOWN': '⚪'
    }
    return status_colors.get(status.upper(), '⚪')

def format_percentage_with_color(value: float) -> str:
    """Format percentage with color indicator."""
    if value >= 95:
        return f"🟢 {value:.1f}%"
    elif value >= 80:
        return f"🟡 {value:.1f}%"
    else:
        return f"🔴 {value:.1f}%"

def format_timedelta(seconds: float) -> str:
    """Format seconds into human-readable time delta."""
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.0f} minutes"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} hours"
    days = hours / 24
    return f"{days:.1f} days"

def format_table_name(table_name: str) -> str:
    """Format table name for display."""
    return table_name.replace('_', ' ').title()

def format_metric_name(metric_name: str) -> str:
    """Format metric name for display."""
    return metric_name.replace('_', ' ').title()

def format_alert_message(alert_type: str, details: Dict[str, Any]) -> str:
    """Format alert message with details."""
    message = alert_type.replace('_', ' ').title()
    
    if 'value' in details:
        message += f": {details['value']:.1f}%"
    
    if 'threshold' in details:
        message += f" (Threshold: {details['threshold']:.1f}%)"
    
    if 'table' in details:
        message += f" - Table: {details['table']}"
    
    return message