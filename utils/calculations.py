"""
Calculation utilities for metrics.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

def calculate_moving_average(values: List[float], window: int = 7) -> List[float]:
    """Calculate moving average of a list of values."""
    if len(values) < window:
        return values
    
    moving_avg = []
    for i in range(len(values) - window + 1):
        avg = sum(values[i:i+window]) / window
        moving_avg.append(avg)
    
    return moving_avg

def calculate_standard_deviation(values: List[float]) -> float:
    """Calculate standard deviation of values."""
    if len(values) < 2:
        return 0.0
    return np.std(values)

def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted score from multiple components."""
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(score * weights.get(key, 0) for key, score in scores.items())
    return weighted_sum / total_weight

def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate between two values."""
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence interval for a list of values."""
    if len(values) < 2:
        return (0.0, 0.0)
    
    mean = np.mean(values)
    std = np.std(values)
    n = len(values)
    
    # Z-score for confidence level
    z_score = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }.get(confidence, 1.96)
    
    margin = z_score * (std / np.sqrt(n))
    return (mean - margin, mean + margin)

def calculate_trend(data: List[float]) -> str:
    """Determine trend direction of data."""
    if len(data) < 2:
        return "stable"
    
    # Simple linear regression slope
    x = np.arange(len(data))
    slope = np.polyfit(x, data, 1)[0]
    
    if slope > 0.1:
        return "increasing"
    elif slope < -0.1:
        return "decreasing"
    else:
        return "stable"

def calculate_anomaly_score(value: float, mean: float, std: float) -> float:
    """Calculate anomaly score using z-score."""
    if std == 0:
        return 0.0
    return abs(value - mean) / std

def calculate_seasonal_index(data: List[float], period: int) -> List[float]:
    """Calculate seasonal indices for periodic data."""
    if len(data) < period * 2:
        return []
    
    seasonal_indices = []
    for i in range(period):
        values = data[i::period]
        if len(values) > 1:
            seasonal_indices.append(np.mean(values))
        else:
            seasonal_indices.append(0)
    
    if seasonal_indices:
        seasonal_indices = np.array(seasonal_indices)
        seasonal_indices = seasonal_indices / np.mean(seasonal_indices)
    
    return seasonal_indices.tolist()