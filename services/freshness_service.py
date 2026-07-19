"""
Data freshness validation service.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text

from database.database import get_db_session
from utils.logger import get_logger

logger = get_logger()

class FreshnessService:
    """Service for data freshness validation."""
    
    def __init__(self):
        self.session = get_db_session()
        
    def validate_freshness(self, table_name: str) -> Dict[str, Any]:
        """Validate data freshness for a specific table."""
        try:
            source_latest = self._get_latest_timestamp(f'source_{table_name}')
            warehouse_latest = self._get_latest_timestamp(f'warehouse_{table_name}')
            
            if source_latest and warehouse_latest:
                # Convert to datetime if they are strings
                if isinstance(source_latest, str):
                    source_latest = datetime.fromisoformat(source_latest.replace('Z', '+00:00'))
                if isinstance(warehouse_latest, str):
                    warehouse_latest = datetime.fromisoformat(warehouse_latest.replace('Z', '+00:00'))
                
                # Calculate delay
                delay_seconds = (warehouse_latest - source_latest).total_seconds()
                delay_minutes = delay_seconds / 60
                
                # Calculate freshness percentage (diminishing returns after 60 minutes)
                if delay_minutes <= 5:
                    freshness_percentage = 100.0
                elif delay_minutes <= 60:
                    freshness_percentage = 100.0 - (delay_minutes / 60) * 5
                else:
                    freshness_percentage = max(0.0, 95.0 - (delay_minutes - 60) * 0.1)
                freshness_percentage = min(100.0, max(0.0, freshness_percentage))
            else:
                delay_minutes = None
                freshness_percentage = 0.0
            
            status = self._determine_status(freshness_percentage)
            
            return {
                'table_name': table_name,
                'source_latest': source_latest.isoformat() if source_latest else None,
                'warehouse_latest': warehouse_latest.isoformat() if warehouse_latest else None,
                'delay_minutes': delay_minutes,
                'delay_hours': delay_minutes / 60 if delay_minutes else None,
                'freshness_percentage': freshness_percentage,
                'status': status,
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating freshness for {table_name}: {str(e)}")
            raise
    
    def validate_all_tables(self) -> Dict[str, Any]:
        """Validate freshness for all tables."""
        tables = ['orders', 'customers', 'events']
        results = {}
        
        for table in tables:
            results[table] = self.validate_freshness(table)
        
        # Calculate overall freshness
        freshness_values = [r['freshness_percentage'] for r in results.values()]
        overall_freshness = sum(freshness_values) / len(freshness_values) if freshness_values else 0.0
        
        return {
            'tables': results,
            'overall_freshness': overall_freshness,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _get_latest_timestamp(self, table_name: str) -> Optional[datetime]:
        """Get the latest timestamp from a table."""
        try:
            # Try different timestamp column names
            timestamp_columns = ['warehouse_timestamp', 'source_timestamp', 'event_timestamp', 
                               'order_date', 'created_at', 'timestamp']
            
            for col in timestamp_columns:
                try:
                    query = text(f"SELECT MAX({col}) as latest FROM {table_name}")
                    result = self.session.execute(query).fetchone()
                    if result and result[0] is not None:
                        # If it's a string, convert to datetime
                        val = result[0]
                        if isinstance(val, str):
                            try:
                                return datetime.fromisoformat(val.replace('Z', '+00:00'))
                            except:
                                # Try alternative format
                                from dateutil import parser
                                return parser.parse(val)
                        return val
                except Exception as e:
                    logger.debug(f"Could not query {col} from {table_name}: {str(e)}")
                    continue
            return None
        except Exception as e:
            logger.error(f"Error getting latest timestamp from {table_name}: {str(e)}")
            return None
    
    def _determine_status(self, freshness: float) -> str:
        """Determine status based on freshness percentage."""
        if freshness >= 95.0:
            return "PASS"
        elif freshness >= 80.0:
            return "WARNING"
        else:
            return "FAIL"