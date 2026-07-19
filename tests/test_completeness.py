"""
Unit tests for completeness service.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime

from services.completeness_service import CompletenessService
from database.database import get_db_session

class TestCompletenessService:
    """Test completeness service functionality."""
    
    @pytest.fixture
    def completeness_service(self):
        """Create completeness service instance."""
        return CompletenessService()
    
    @patch('services.completeness_service.get_db_session')
    def test_validate_completeness_success(self, mock_session, completeness_service):
        """Test successful completeness validation."""
        # Mock database session
        mock_session.return_value = Mock()
        
        # Mock query results
        mock_session.return_value.execute.return_value.fetchone.return_value = (100,)
        
        result = completeness_service.validate_completeness('orders')
        
        assert result['table_name'] == 'orders'
        assert result['source_count'] == 100
        assert result['warehouse_count'] == 100
        assert result['completeness_percentage'] == 100.0
        assert result['status'] == 'PASS'
    
    @patch('services.completeness_service.get_db_session')
    def test_validate_completeness_missing_records(self, mock_session, completeness_service):
        """Test completeness validation with missing records."""
        # Mock database session
        mock_session.return_value = Mock()
        
        # Mock query results - source has 100, warehouse has 85
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (100,)
                    else:
                        return (85,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = completeness_service.validate_completeness('orders')
        
        assert result['table_name'] == 'orders'
        assert result['source_count'] == 100
        assert result['warehouse_count'] == 85
        assert result['missing_records'] == 15
        assert result['completeness_percentage'] == 85.0
        assert result['status'] == 'FAIL'
    
    @patch('services.completeness_service.get_db_session')
    def test_validate_completeness_warning(self, mock_session, completeness_service):
        """Test completeness validation with warning status."""
        mock_session.return_value = Mock()
        
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (100,)
                    else:
                        return (97,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = completeness_service.validate_completeness('orders')
        
        assert result['completeness_percentage'] == 97.0
        assert result['status'] == 'WARNING'
    
    @patch('services.completeness_service.get_db_session')
    def test_validate_all_tables(self, mock_session, completeness_service):
        """Test validation of all tables."""
        mock_session.return_value = Mock()
        
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (100,)
                    else:
                        return (95,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = completeness_service.validate_all_tables()
        
        assert 'tables' in result
        assert 'overall_completeness' in result
        assert len(result['tables']) == 3
        assert 'validation_timestamp' in result
    
    def test_determine_status(self, completeness_service):
        """Test status determination logic."""
        assert completeness_service._determine_status(99.5) == 'PASS'
        assert completeness_service._determine_status(97.0) == 'WARNING'
        assert completeness_service._determine_status(89.0) == 'FAIL'
        assert completeness_service._determine_status(95.0) == 'WARNING'
        assert completeness_service._determine_status(99.0) == 'PASS'
    
    def test_get_business_impact(self, completeness_service):
        """Test business impact descriptions."""
        assert 'Critical' in completeness_service._get_business_impact(75.0)
        assert 'Significant' in completeness_service._get_business_impact(88.0)
        assert 'Minor' in completeness_service._get_business_impact(93.0)
        assert 'Excellent' in completeness_service._get_business_impact(99.5)