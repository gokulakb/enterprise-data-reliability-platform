"""
Alert service for data reliability monitoring.
"""
from typing import Dict, Any, List
from datetime import datetime

from utils.logger import get_logger

logger = get_logger()

class AlertService:
    """Service for generating and managing alerts."""
    
    def __init__(self):
        self.alerts = []
    
    def check_completeness_alert(self, completeness_data: Dict[str, Any]) -> List[Dict]:
        """Check for completeness alerts."""
        alerts = []
        
        for table, data in completeness_data.get('tables', {}).items():
            if data['completeness_percentage'] < 95:
                alerts.append({
                    'severity': 'WARNING',
                    'type': 'completeness_low',
                    'table': table,
                    'value': data['completeness_percentage'],
                    'threshold': 95,
                    'message': f"Completeness for {table} is {data['completeness_percentage']:.1f}% (below 95%)",
                    'timestamp': datetime.now().isoformat()
                })
            
            if data['completeness_percentage'] < 90:
                alerts.append({
                    'severity': 'CRITICAL',
                    'type': 'completeness_critical',
                    'table': table,
                    'value': data['completeness_percentage'],
                    'threshold': 90,
                    'message': f"Critical: Completeness for {table} is {data['completeness_percentage']:.1f}% (below 90%)",
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def check_freshness_alert(self, freshness_data: Dict[str, Any]) -> List[Dict]:
        """Check for freshness alerts."""
        alerts = []
        
        for table, data in freshness_data.get('tables', {}).items():
            delay = data.get('delay_minutes', 0)
            
            if delay and delay > 60:
                alerts.append({
                    'severity': 'WARNING',
                    'type': 'freshness_delay',
                    'table': table,
                    'value': delay,
                    'threshold': 60,
                    'message': f"Freshness delay for {table}: {delay:.1f} minutes",
                    'timestamp': datetime.now().isoformat()
                })
            
            if delay and delay > 120:
                alerts.append({
                    'severity': 'CRITICAL',
                    'type': 'freshness_critical',
                    'table': table,
                    'value': delay,
                    'threshold': 120,
                    'message': f"Critical: Freshness delay for {table}: {delay:.1f} minutes",
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def check_reconciliation_alert(self, reconciliation_data: Dict[str, Any]) -> List[Dict]:
        """Check for reconciliation alerts."""
        alerts = []
        
        for table, data in reconciliation_data.get('tables', {}).items():
            if 'match_percentage' in data:
                match = data['match_percentage']
                
                if match < 95:
                    alerts.append({
                        'severity': 'WARNING',
                        'type': 'reconciliation_mismatch',
                        'table': table,
                        'value': match,
                        'threshold': 95,
                        'message': f"Reconciliation mismatch for {table}: {match:.1f}% match",
                        'timestamp': datetime.now().isoformat()
                    })
                
                if match < 90:
                    alerts.append({
                        'severity': 'CRITICAL',
                        'type': 'reconciliation_critical',
                        'table': table,
                        'value': match,
                        'threshold': 90,
                        'message': f"Critical: Reconciliation mismatch for {table}: {match:.1f}% match",
                        'timestamp': datetime.now().isoformat()
                    })
        
        return alerts
    
    def check_pipeline_alert(self, pipeline_data: Dict[str, Any]) -> List[Dict]:
        """Check for pipeline alerts."""
        alerts = []
        
        success_rate = pipeline_data.get('success_rate', 0)
        
        if success_rate < 85:
            alerts.append({
                'severity': 'WARNING',
                'type': 'pipeline_success_low',
                'value': success_rate,
                'threshold': 85,
                'message': f"Pipeline success rate is {success_rate:.1f}% (below 85%)",
                'timestamp': datetime.now().isoformat()
            })
        
        if success_rate < 70:
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'pipeline_success_critical',
                'value': success_rate,
                'threshold': 70,
                'message': f"Critical: Pipeline success rate is {success_rate:.1f}% (below 70%)",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def check_quality_alert(self, quality_data: Dict[str, Any]) -> List[Dict]:
        """Check for quality alerts."""
        alerts = []
        
        score = quality_data.get('quality_score', 0)
        
        if score < 85:
            alerts.append({
                'severity': 'WARNING',
                'type': 'quality_score_low',
                'value': score,
                'threshold': 85,
                'message': f"Quality score is {score:.1f} (below 85)",
                'timestamp': datetime.now().isoformat()
            })
        
        if score < 75:
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'quality_score_critical',
                'value': score,
                'threshold': 75,
                'message': f"Critical: Quality score is {score:.1f} (below 75)",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def generate_all_alerts(self, metrics_data: Dict[str, Any]) -> List[Dict]:
        """Generate all alerts from metrics data."""
        all_alerts = []
        
        if 'completeness' in metrics_data:
            all_alerts.extend(self.check_completeness_alert(metrics_data['completeness']))
        
        if 'freshness' in metrics_data:
            all_alerts.extend(self.check_freshness_alert(metrics_data['freshness']))
        
        if 'reconciliation' in metrics_data:
            all_alerts.extend(self.check_reconciliation_alert(metrics_data['reconciliation']))
        
        if 'pipeline' in metrics_data:
            all_alerts.extend(self.check_pipeline_alert(metrics_data['pipeline']))
        
        if 'quality' in metrics_data:
            all_alerts.extend(self.check_quality_alert(metrics_data['quality']))
        
        # Sort by severity (critical first)
        all_alerts.sort(key=lambda x: 0 if x['severity'] == 'CRITICAL' else 1)
        
        return all_alerts