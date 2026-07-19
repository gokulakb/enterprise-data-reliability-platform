"""
Source to warehouse reconciliation service.
"""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import text

from database.database import get_db_session
from utils.logger import get_logger
from utils.helpers import calculate_percentage
from config.settings import TABLES

logger = get_logger()

class ReconciliationService:
    """Service for source to warehouse reconciliation."""
    
    def __init__(self):
        self.session = get_db_session()
    
    def reconcile_table(self, table_name: str) -> Dict[str, Any]:
        """Reconcile source and warehouse data for a specific table."""
        try:
            pk = TABLES[table_name]['primary_key']
            
            # Load data
            source_data = self._load_table_data(f'source_{table_name}')
            warehouse_data = self._load_table_data(f'warehouse_{table_name}')
            
            if source_data.empty and warehouse_data.empty:
                return {'error': 'No data found for reconciliation'}
            
            source_keys = set(source_data[pk]) if not source_data.empty else set()
            warehouse_keys = set(warehouse_data[pk]) if not warehouse_data.empty else set()
            
            # Find discrepancies
            missing_in_warehouse = source_keys - warehouse_keys
            extra_in_warehouse = warehouse_keys - source_keys
            
            # Find duplicates
            source_duplicates = self._find_duplicates(source_data, pk)
            warehouse_duplicates = self._find_duplicates(warehouse_data, pk)
            
            # Calculate match percentage
            common_keys = source_keys.intersection(warehouse_keys)
            total_keys = len(source_keys.union(warehouse_keys))
            match_percentage = calculate_percentage(len(common_keys), total_keys) if total_keys > 0 else 0
            
            status = self._determine_status(match_percentage)
            
            return {
                'table_name': table_name,
                'primary_key': pk,
                'source_count': len(source_data),
                'warehouse_count': len(warehouse_data),
                'match_count': len(common_keys),
                'match_percentage': match_percentage,
                'missing_in_warehouse': len(missing_in_warehouse),
                'extra_in_warehouse': len(extra_in_warehouse),
                'source_duplicates': len(source_duplicates),
                'warehouse_duplicates': len(warehouse_duplicates),
                'mismatches': 0,
                'status': status,
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reconciling {table_name}: {str(e)}")
            raise
    
    def reconcile_all_tables(self) -> Dict[str, Any]:
        """Reconcile all tables."""
        tables = ['orders', 'customers', 'events']
        results = {}
        
        for table in tables:
            results[table] = self.reconcile_table(table)
        
        match_values = [r['match_percentage'] for r in results.values() if 'match_percentage' in r]
        overall_match = sum(match_values) / len(match_values) if match_values else 0
        
        return {
            'tables': results,
            'overall_match': overall_match,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _load_table_data(self, table_name: str) -> pd.DataFrame:
        """Load data from a table into DataFrame."""
        try:
            query = text(f"SELECT * FROM {table_name}")
            return pd.read_sql(query, self.session.bind)
        except Exception as e:
            logger.error(f"Error loading data from {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def _find_duplicates(self, df: pd.DataFrame, pk: str) -> List[int]:
        """Find duplicate primary keys in a DataFrame."""
        if df.empty or pk not in df.columns:
            return []
        duplicate_keys = df[df.duplicated([pk], keep=False)][pk].tolist()
        return list(set(duplicate_keys))
    
    def _determine_status(self, match_percentage: float) -> str:
        """Determine status based on match percentage."""
        if match_percentage >= 98:
            return "PASS"
        elif match_percentage >= 90:
            return "WARNING"
        else:
            return "FAIL"