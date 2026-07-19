"""
Data quality scoring service.
"""
from typing import Dict, Any
from datetime import datetime

from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.pipeline_health import PipelineHealthService
from utils.logger import get_logger
from config.settings import QUALITY_WEIGHTS

logger = get_logger()

class QualityService:
    """Service for data quality scoring."""
    
    def __init__(self):
        self.completeness_service = CompletenessService()
        self.freshness_service = FreshnessService()
        self.reconciliation_service = ReconciliationService()
        self.pipeline_health = PipelineHealthService()
        
    def calculate_quality_score(self) -> Dict[str, Any]:
        """Calculate overall data quality score."""
        try:
            # Get all metrics
            completeness = self.completeness_service.validate_all_tables()
            freshness = self.freshness_service.validate_all_tables()
            reconciliation = self.reconciliation_service.reconcile_all_tables()
            pipeline = self.pipeline_health.get_pipeline_status()
            
            # Calculate weighted scores
            weights = QUALITY_WEIGHTS
            
            completeness_score = completeness['overall_completeness']
            freshness_score = freshness['overall_freshness']
            reconciliation_score = reconciliation['overall_match']
            pipeline_score = pipeline.get('success_rate', 0)
            
            # Apply weights
            quality_score = (
                completeness_score * weights['completeness'] +
                freshness_score * weights['freshness'] +
                reconciliation_score * weights['reconciliation'] +
                pipeline_score * weights['pipeline_health']
            )
            
            # Determine quality tier
            quality_tier = self._determine_tier(quality_score)
            
            return {
                'quality_score': round(quality_score, 2),
                'quality_tier': quality_tier,
                'components': {
                    'completeness': {
                        'score': completeness_score,
                        'weight': weights['completeness'],
                        'weighted_score': completeness_score * weights['completeness']
                    },
                    'freshness': {
                        'score': freshness_score,
                        'weight': weights['freshness'],
                        'weighted_score': freshness_score * weights['freshness']
                    },
                    'reconciliation': {
                        'score': reconciliation_score,
                        'weight': weights['reconciliation'],
                        'weighted_score': reconciliation_score * weights['reconciliation']
                    },
                    'pipeline_health': {
                        'score': pipeline_score,
                        'weight': weights['pipeline_health'],
                        'weighted_score': pipeline_score * weights['pipeline_health']
                    }
                },
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            raise
    
    def _determine_tier(self, score: float) -> str:
        """Determine quality tier based on score."""
        if score >= 95:
            return "EXCELLENT"
        elif score >= 85:
            return "GOOD"
        elif score >= 75:
            return "FAIR"
        else:
            return "POOR"