"""
Data reliability sign-off service.
"""
from typing import Dict, Any
from datetime import datetime

from services.quality_service import QualityService
from services.pipeline_health import PipelineHealthService
from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from utils.logger import get_logger

logger = get_logger()

class SignOffService:
    """Service for data reliability sign-off."""
    
    def __init__(self):
        self.quality_service = QualityService()
        self.pipeline_health = PipelineHealthService()
        self.completeness_service = CompletenessService()
        self.freshness_service = FreshnessService()
        self.reconciliation_service = ReconciliationService()
        
    def generate_sign_off(self) -> Dict[str, Any]:
        """Generate data reliability sign-off report."""
        try:
            # Get all metrics
            quality = self.quality_service.calculate_quality_score()
            pipeline = self.pipeline_health.get_pipeline_status()
            completeness = self.completeness_service.validate_all_tables()
            freshness = self.freshness_service.validate_all_tables()
            reconciliation = self.reconciliation_service.reconcile_all_tables()
            
            # Evaluate sign-off status
            sign_off_status = self._evaluate_sign_off(
                quality['quality_score'],
                freshness['overall_freshness'],
                completeness['overall_completeness'],
                pipeline.get('success_rate', 0)
            )
            
            return {
                'sign_off_status': sign_off_status,
                'quality_score': quality['quality_score'],
                'quality_tier': quality['quality_tier'],
                'pipeline_health': pipeline.get('status', 'UNKNOWN'),
                'freshness_score': freshness['overall_freshness'],
                'completeness_score': completeness['overall_completeness'],
                'reconciliation_score': reconciliation['overall_match'],
                'sign_off_timestamp': datetime.now().isoformat(),
                'recommendations': self._get_recommendations(sign_off_status, quality, pipeline)
            }
            
        except Exception as e:
            logger.error(f"Error generating sign-off: {str(e)}")
            raise
    
    def _evaluate_sign_off(self, quality_score: float, freshness: float, 
                          completeness: float, pipeline_success: float) -> str:
        """Evaluate sign-off status based on all metrics."""
        if (quality_score >= 98 and freshness >= 95 and 
            completeness >= 99 and pipeline_success >= 95):
            return "PASS"
        elif (quality_score >= 90 and freshness >= 85 and 
              completeness >= 90 and pipeline_success >= 85):
            return "WARNING"
        else:
            return "FAIL"
    
    def _get_recommendations(self, status: str, quality: Dict, pipeline: Dict) -> list:
        """Get recommendations based on sign-off status."""
        recommendations = []
        
        if status == "FAIL":
            recommendations.append("URGENT: Critical data quality issues detected")
            
            if quality['quality_score'] < 90:
                recommendations.append("Review and fix completeness, freshness, and reconciliation gaps")
            
            if pipeline.get('success_rate', 0) < 85:
                recommendations.append("Investigate pipeline failures and implement fixes")
        
        elif status == "WARNING":
            if quality['quality_score'] < 95:
                recommendations.append("Address minor quality issues before next sign-off")
            
            if pipeline.get('success_rate', 0) < 90:
                recommendations.append("Monitor pipeline performance and address intermittent failures")
        
        else:  # PASS
            recommendations.append("All data quality metrics are within acceptable ranges")
            recommendations.append("Maintain current monitoring and validation processes")
        
        return recommendations