"""
Helper functions for common operations.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import random

from utils.logger import get_logger

logger = get_logger()

def generate_timestamp(days_back: int = 30) -> datetime:
    """Generate a random timestamp within the last N days."""
    start = datetime.now() - timedelta(days=days_back)
    return start + timedelta(seconds=random.randint(0, days_back * 86400))

def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage with proper handling of zero division."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)

def is_valid_date(date_str: str) -> bool:
    """Check if a string is a valid date."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def format_currency(value: float) -> str:
    """Format number as currency."""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.1f}%"

def format_number(value: float) -> str:
    """Format number with commas."""
    return f"{value:,.0f}"

def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, returning 0 if denominator is 0."""
    if denominator == 0:
        return 0.0
    return numerator / denominator

def parse_json_safe(json_str: str) -> Dict:
    """Safely parse JSON string."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def create_empty_dataframe(columns: List[str]) -> pd.DataFrame:
    """Create an empty DataFrame with specified columns."""
    return pd.DataFrame(columns=columns)

def get_business_impact_description(metric: str, value: float) -> str:
    """Get business impact description based on metric value."""
    impacts = {
        'completeness': {
            (0, 80): "Critical data loss affecting all downstream analytics",
            (80, 90): "Significant data gaps impacting reporting accuracy",
            (90, 95): "Minor data gaps may affect detailed analysis",
            (95, 99): "Good completeness with minimal gaps",
            (99, 101): "Excellent completeness - data is reliable"
        },
        'freshness': {
            (0, 60): "Extreme delays making data unusable for operational decisions",
            (60, 75): "Major delays impacting time-sensitive decisions",
            (75, 85): "Moderate delays affecting some time-critical reports",
            (85, 95): "Good freshness for most use cases",
            (95, 101): "Excellent freshness - data is current"
        }
    }
    
    metric_impacts = impacts.get(metric, {})
    for (lower, upper), description in metric_impacts.items():
        if lower <= value < upper:
            return description
    return "Data reliability status requires attention"