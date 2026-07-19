"""
Centralized metrics service.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.anomaly_detection import AnomalyDetectionService
from services.pipeline_health import PipelineHealthService
from database.database import get_db_session
from utils.logger import get_logger
from config.settings import QUALITY_WEIGHTS

logger = get_logger()

class MetricsService:
    """Centralized service for all metrics."""
    
    def __init__(self):
        self.session = get_db_session()
        self.completeness_service = CompletenessService()
        self.freshness_service = FreshnessService()
        self.reconciliation_service = ReconciliationService()
        self.pipeline_service = PipelineHealthService()
        self.anomaly_service = AnomalyDetectionService()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics in one call."""
        try:
            completeness = self.completeness_service.validate_all_tables()
            freshness = self.freshness_service.validate_all_tables()
            reconciliation = self.reconciliation_service.reconcile_all_tables()
            pipeline = self.pipeline_service.get_pipeline_status()
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                completeness['overall_completeness'],
                freshness['overall_freshness'],
                reconciliation['overall_match'],
                pipeline.get('success_rate', 0)
            )
            
            return {
                'completeness': completeness,
                'freshness': freshness,
                'reconciliation': reconciliation,
                'pipeline': pipeline,
                'quality_score': quality_score,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting all metrics: {str(e)}")
            raise
    
    def _calculate_quality_score(self, completeness: float, freshness: float, 
                                 reconciliation: float, pipeline_health: float) -> Dict[str, Any]:
        """Calculate overall quality score."""
        weights = QUALITY_WEIGHTS
        
        weighted_score = (
            completeness * weights['completeness'] +
            freshness * weights['freshness'] +
            reconciliation * weights['reconciliation'] +
            pipeline_health * weights['pipeline_health']
        )
        
        return {
            'score': round(weighted_score, 2),
            'components': {
                'completeness': completeness,
                'freshness': freshness,
                'reconciliation': reconciliation,
                'pipeline_health': pipeline_health
            },
            'weights': weights
        }
    
    def get_audit_logs(self, limit: int = 100) -> pd.DataFrame:
        """Get recent audit logs."""
        try:
            query = """
                SELECT timestamp, user, action, metric_type, metric_value, status, details
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT :limit
            """
            df = pd.read_sql(query, self.session.bind, params={'limit': limit})
            return df
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return pd.DataFrame()