"""
Data completeness validation service.
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text

from database.database import get_db_session
from utils.logger import get_logger
from utils.helpers import calculate_percentage

logger = get_logger()

class CompletenessService:
    """Service for data completeness validation."""
    
    def __init__(self):
        self.session = get_db_session()
        
    def validate_completeness(self, table_name: str) -> Dict[str, Any]:
        """Validate completeness for a specific table."""
        try:
            source_count = self._get_record_count(f'source_{table_name}')
            warehouse_count = self._get_record_count(f'warehouse_{table_name}')
            
            completeness_percentage = calculate_percentage(warehouse_count, source_count)
            
            status = self._determine_status(completeness_percentage)
            business_impact = self._get_business_impact(completeness_percentage)
            
            return {
                'table_name': table_name,
                'source_count': source_count,
                'warehouse_count': warehouse_count,
                'missing_records': source_count - warehouse_count,
                'completeness_percentage': completeness_percentage,
                'status': status,
                'business_impact': business_impact,
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating completeness for {table_name}: {str(e)}")
            raise
    
    def validate_all_tables(self) -> Dict[str, Any]:
        """Validate completeness for all tables."""
        tables = ['orders', 'customers', 'events']
        results = {}
        
        for table in tables:
            results[table] = self.validate_completeness(table)
        
        completeness_values = [r['completeness_percentage'] for r in results.values()]
        overall_completeness = sum(completeness_values) / len(completeness_values)
        
        return {
            'tables': results,
            'overall_completeness': overall_completeness,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _get_record_count(self, table_name: str) -> int:
        """Get record count from a table."""
        try:
            query = text(f"SELECT COUNT(*) as count FROM {table_name}")
            result = self.session.execute(query).fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting record count from {table_name}: {str(e)}")
            return 0
    
    def _determine_status(self, completeness: float) -> str:
        """Determine status based on completeness percentage."""
        if completeness >= 99:
            return "PASS"
        elif completeness >= 95:
            return "WARNING"
        else:
            return "FAIL"
    
    def _get_business_impact(self, completeness: float) -> str:
        """Get business impact description."""
        if completeness >= 99:
            return "All expected data is present - high confidence in reporting"
        elif completeness >= 95:
            return "Minor data gaps that may affect detailed analysis"
        elif completeness >= 85:
            return "Significant data gaps impacting accuracy of key metrics"
        else:
            return "Critical data loss affecting all downstream analytics"