"""
Pipeline health monitoring service.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import text

from database.database import get_db_session
from database.models import PipelineRun
from utils.logger import get_logger
from utils.helpers import calculate_percentage

logger = get_logger()

class PipelineHealthService:
    """Service for pipeline health monitoring."""
    
    def __init__(self):
        self.session = get_db_session()
        
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline health status."""
        try:
            pipeline_runs = self._get_recent_runs()
            
            if not pipeline_runs:
                return {
                    'total_runs': 0,
                    'status': 'UNKNOWN',
                    'message': 'No pipeline runs found'
                }
            
            total_runs = len(pipeline_runs)
            successful_runs = sum(1 for run in pipeline_runs if run.status == 'success')
            failed_runs = sum(1 for run in pipeline_runs if run.status == 'failed')
            running_runs = sum(1 for run in pipeline_runs if run.status == 'running')
            
            success_rate = calculate_percentage(successful_runs, total_runs)
            
            return {
                'total_runs': total_runs,
                'successful_runs': successful_runs,
                'failed_runs': failed_runs,
                'running_runs': running_runs,
                'success_rate': success_rate,
                'delayed_runs': 0,
                'delay_percentage': 0,
                'latest_run': self._get_latest_run_info(pipeline_runs),
                'status': self._determine_health_status(success_rate),
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline health: {str(e)}")
            raise
    
    def get_pipeline_details(self, pipeline_name: str = None) -> Dict[str, Any]:
        """Get detailed health for a specific pipeline."""
        try:
            query = self.session.query(PipelineRun)
            if pipeline_name:
                query = query.filter(PipelineRun.pipeline_name == pipeline_name)
            
            runs = query.order_by(PipelineRun.start_time.desc()).limit(100).all()
            
            if not runs:
                return {'error': 'No pipeline runs found'}
            
            total_runs = len(runs)
            successful = sum(1 for r in runs if r.status == 'success')
            failed = sum(1 for r in runs if r.status == 'failed')
            
            return {
                'pipeline_name': pipeline_name or 'all',
                'total_runs': total_runs,
                'successful': successful,
                'failed': failed,
                'success_rate': calculate_percentage(successful, total_runs),
                'status': self._determine_health_status(calculate_percentage(successful, total_runs)),
                'recent_runs': [
                    {
                        'run_id': r.run_id,
                        'start_time': r.start_time.isoformat() if r.start_time else None,
                        'end_time': r.end_time.isoformat() if r.end_time else None,
                        'status': r.status,
                        'records': r.records_processed,
                        'error': r.error_message
                    }
                    for r in runs[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline details: {str(e)}")
            raise
    
    def _get_recent_runs(self, hours: int = 24) -> List[PipelineRun]:
        """Get recent pipeline runs."""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            return self.session.query(PipelineRun).filter(
                PipelineRun.start_time >= cutoff
            ).order_by(PipelineRun.start_time.desc()).limit(100).all()
        except Exception as e:
            logger.error(f"Error getting recent runs: {str(e)}")
            return []
    
    def _get_latest_run_info(self, runs: List[PipelineRun]) -> Dict[str, Any]:
        """Get information about the latest run."""
        if not runs:
            return {}
        
        latest = runs[0]
        return {
            'run_id': latest.run_id,
            'pipeline_name': latest.pipeline_name,
            'start_time': latest.start_time.isoformat() if latest.start_time else None,
            'status': latest.status,
            'records_processed': latest.records_processed
        }
    
    def _determine_health_status(self, success_rate: float) -> str:
        """Determine overall health status."""
        if success_rate >= 95:
            return "HEALTHY"
        elif success_rate >= 85:
            return "WARNING"
        else:
            return "CRITICAL"