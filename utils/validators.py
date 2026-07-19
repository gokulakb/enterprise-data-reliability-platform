"""
Data validation utilities.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime

from utils.logger import get_logger

logger = get_logger()

class DataValidator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> Dict[str, Any]:
        """Validate DataFrame schema."""
        missing_columns = [col for col in expected_columns if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in expected_columns]
        
        return {
            'valid': len(missing_columns) == 0,
            'missing_columns': missing_columns,
            'extra_columns': extra_columns,
            'expected_columns': expected_columns,
            'actual_columns': list(df.columns)
        }
    
    @staticmethod
    def validate_null_values(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Validate null values in DataFrame."""
        null_counts = {}
        null_percentages = {}
        
        for col in columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                null_pct = (null_count / len(df)) * 100
                null_counts[col] = null_count
                null_percentages[col] = null_pct
        
        return {
            'null_counts': null_counts,
            'null_percentages': null_percentages,
            'has_nulls': any(v > 0 for v in null_counts.values())
        }
    
    @staticmethod
    def validate_duplicates(df: pd.DataFrame, key_columns: List[str]) -> Dict[str, Any]:
        """Validate duplicate records."""
        if not all(col in df.columns for col in key_columns):
            return {'error': 'Key columns not found in DataFrame'}
        
        duplicate_groups = df.groupby(key_columns).filter(lambda x: len(x) > 1)
        duplicate_count = len(duplicate_groups)
        
        return {
            'duplicate_count': duplicate_count,
            'duplicate_percentage': (duplicate_count / len(df)) * 100 if len(df) > 0 else 0,
            'has_duplicates': duplicate_count > 0,
            'sample_duplicates': duplicate_groups.head(10).to_dict('records')
        }
    
    @staticmethod
    def validate_timestamps(df: pd.DataFrame, timestamp_col: str) -> Dict[str, Any]:
        """Validate timestamp column."""
        if timestamp_col not in df.columns:
            return {'error': f'Timestamp column {timestamp_col} not found'}
        
        try:
            timestamps = pd.to_datetime(df[timestamp_col])
            min_ts = timestamps.min()
            max_ts = timestamps.max()
            range_seconds = (max_ts - min_ts).total_seconds()
            
            return {
                'valid': True,
                'min_timestamp': min_ts.isoformat(),
                'max_timestamp': max_ts.isoformat(),
                'range_seconds': range_seconds,
                'range_hours': range_seconds / 3600,
                'range_days': range_seconds / 86400
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}