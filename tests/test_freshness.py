"""
Unit tests for freshness service.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from services.freshness_service import FreshnessService

class TestFreshnessService:
    """Test freshness service functionality."""
    
    @pytest.fixture
    def freshness_service(self):
        """Create freshness service instance."""
        return FreshnessService()
    
    @patch('services.freshness_service.get_db_session')
    def test_validate_freshness_success(self, mock_session, freshness_service):
        """Test successful freshness validation."""
        mock_session.return_value = Mock()
        
        # Mock timestamps
        source_time = datetime.now() - timedelta(minutes=5)
        warehouse_time = datetime.now()
        
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (source_time,)
                    else:
                        return (warehouse_time,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = freshness_service.validate_freshness('orders')
        
        assert result['table_name'] == 'orders'
        assert result['delay_minutes'] == 5.0
        assert result['freshness_percentage'] == 100.0
        assert result['status'] == 'PASS'
    
    @patch('services.freshness_service.get_db_session')
    def test_validate_freshness_delay(self, mock_session, freshness_service):
        """Test freshness validation with delay."""
        mock_session.return_value = Mock()
        
        source_time = datetime.now() - timedelta(hours=2)
        warehouse_time = datetime.now()
        
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (source_time,)
                    else:
                        return (warehouse_time,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = freshness_service.validate_freshness('orders')
        
        assert result['delay_minutes'] == 120.0
        assert result['freshness_percentage'] < 95
        assert result['status'] == 'FAIL'
    
    @patch('services.freshness_service.get_db_session')
    def test_validate_all_tables(self, mock_session, freshness_service):
        """Test validation of all tables."""
        mock_session.return_value = Mock()
        
        current_time = datetime.now()
        
        def mock_execute(query):
            class Result:
                def fetchone(self):
                    if 'source' in str(query):
                        return (current_time - timedelta(minutes=10),)
                    else:
                        return (current_time,)
            return Result()
        
        mock_session.return_value.execute.side_effect = mock_execute
        
        result = freshness_service.validate_all_tables()
        
        assert 'tables' in result
        assert 'overall_freshness' in result
        assert len(result['tables']) == 3
    
    def test_determine_status(self, freshness_service):
        """Test status determination logic."""
        assert freshness_service._determine_status(97.0) == 'PASS'
        assert freshness_service._determine_status(90.0) == 'WARNING'
        assert freshness_service._determine_status(75.0) == 'FAIL'
        assert freshness_service._determine_status(95.0) == 'PASS'
        assert freshness_service._determine_status(80.0) == 'WARNING'
    
    def test_get_latest_timestamp_missing(self, freshness_service):
        """Test getting latest timestamp from missing table."""
        result = freshness_service._get_latest_timestamp('non_existent_table')
        assert result is None