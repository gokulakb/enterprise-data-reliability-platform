"""
Anomaly detection service for data reliability.
"""
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from utils.logger import get_logger

logger = get_logger()

class AnomalyDetectionService:
    """Service for detecting anomalies in data metrics."""
    
    def __init__(self):
        self.anomaly_threshold = 2.5  # Standard deviations for anomaly detection
    
    def detect_completeness_anomalies(self, historical_data: List[float]) -> Dict[str, Any]:
        """Detect anomalies in completeness metrics."""
        if len(historical_data) < 10:
            return {'anomalies': [], 'confidence': 'low', 'message': 'Insufficient data for anomaly detection'}
        
        mean = np.mean(historical_data)
        std = np.std(historical_data)
        
        anomalies = []
        for i, value in enumerate(historical_data):
            z_score = (value - mean) / std if std > 0 else 0
            if abs(z_score) > self.anomaly_threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'z_score': z_score,
                    'expected_range': f"{mean - 2*std:.1f} - {mean + 2*std:.1f}"
                })
        
        return {
            'anomalies': anomalies,
            'mean': mean,
            'std': std,
            'confidence': 'high' if len(historical_data) >= 30 else 'medium',
            'anomaly_count': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_freshness_anomalies(self, delay_data: List[float]) -> Dict[str, Any]:
        """Detect anomalies in freshness delays."""
        if len(delay_data) < 10:
            return {'anomalies': [], 'confidence': 'low', 'message': 'Insufficient data for anomaly detection'}
        
        # Use IQR method for delay anomalies
        q1 = np.percentile(delay_data, 25)
        q3 = np.percentile(delay_data, 75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        
        anomalies = []
        for i, delay in enumerate(delay_data):
            if delay > upper_bound:
                anomalies.append({
                    'index': i,
                    'delay_minutes': delay,
                    'threshold': upper_bound,
                    'severity': 'critical' if delay > 3 * upper_bound else 'warning'
                })
        
        return {
            'anomalies': anomalies,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'upper_bound': upper_bound,
            'anomaly_count': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_value_distribution_anomalies(self, values: List[float]) -> Dict[str, Any]:
        """Detect anomalies in value distributions."""
        if len(values) < 10:
            return {'anomalies': [], 'confidence': 'low', 'message': 'Insufficient data for anomaly detection'}
        
        mean = np.mean(values)
        std = np.std(values)
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = (value - mean) / std if std > 0 else 0
            if abs(z_score) > self.anomaly_threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'z_score': z_score,
                    'expected_range': f"{mean - 2*std:.1f} - {mean + 2*std:.1f}"
                })
        
        return {
            'anomalies': anomalies,
            'mean': mean,
            'std': std,
            'anomaly_count': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }