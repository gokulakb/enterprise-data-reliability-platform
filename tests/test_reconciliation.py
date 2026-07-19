"""
Unit tests for reconciliation service.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from services.reconciliation_service import ReconciliationService

class TestReconciliationService:
    """Test reconciliation service functionality."""
    
    @pytest.fixture
    def reconciliation_service(self):
        """Create reconciliation service instance."""
        return ReconciliationService()
    
    @patch('services.reconciliation_service.get_db_session')
    def test_reconcile_table_success(self, mock_session, reconciliation_service):
        """Test successful reconciliation."""
        mock_session.return_value = Mock()
        
        # Mock data frames
        source_df = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': [100, 101, 102, 103, 104],
            'amount': [100, 200, 300, 400, 500]
        })
        
        warehouse_df = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': [100, 101, 102, 103, 104],
            'amount': [100, 200, 300, 400, 500]
        })
        
        with patch('services.reconciliation_service.ReconciliationService._load_table_data') as mock_load:
            mock_load.side_effect = [source_df, warehouse_df]
            
            result = reconciliation_service.reconcile_table('orders')
            
            assert result['table_name'] == 'orders'
            assert result['source_count'] == 5
            assert result['warehouse_count'] == 5
            assert result['match_percentage'] == 100.0
            assert result['status'] == 'PASS'
    
    @patch('services.reconciliation_service.get_db_session')
    def test_reconcile_table_missing_records(self, mock_session, reconciliation_service):
        """Test reconciliation with missing records."""
        mock_session.return_value = Mock()
        
        source_df = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': [100, 101, 102, 103, 104],
            'amount': [100, 200, 300, 400, 500]
        })
        
        warehouse_df = pd.DataFrame({
            'order_id': [1, 2, 3],
            'customer_id': [100, 101, 102],
            'amount': [100, 200, 300]
        })
        
        with patch('services.reconciliation_service.ReconciliationService._load_table_data') as mock_load:
            mock_load.side_effect = [source_df, warehouse_df]
            
            result = reconciliation_service.reconcile_table('orders')
            
            assert result['source_count'] == 5
            assert result['warehouse_count'] == 3
            assert result['missing_in_warehouse'] == 2
            assert result['match_percentage'] == 60.0
            assert result['status'] == 'FAIL'
    
    @patch('services.reconciliation_service.get_db_session')
    def test_reconcile_table_extra_records(self, mock_session, reconciliation_service):
        """Test reconciliation with extra records."""
        mock_session.return_value = Mock()
        
        source_df = pd.DataFrame({
            'order_id': [1, 2, 3],
            'customer_id': [100, 101, 102],
            'amount': [100, 200, 300]
        })
        
        warehouse_df = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'customer_id': [100, 101, 102, 103, 104],
            'amount': [100, 200, 300, 400, 500]
        })
        
        with patch('services.reconciliation_service.ReconciliationService._load_table_data') as mock_load:
            mock_load.side_effect = [source_df, warehouse_df]
            
            result = reconciliation_service.reconcile_table('orders')
            
            assert result['source_count'] == 3
            assert result['warehouse_count'] == 5
            assert result['extra_in_warehouse'] == 2
            assert result['match_percentage'] == 60.0
    
    @patch('services.reconciliation_service.get_db_session')
    def test_reconcile_all_tables(self, mock_session, reconciliation_service):
        """Test reconciliation of all tables."""
        mock_session.return_value = Mock()
        
        with patch('services.reconciliation_service.ReconciliationService.reconcile_table') as mock_reconcile:
            mock_reconcile.return_value = {
                'match_percentage': 95.0,
                'status': 'PASS'
            }
            
            result = reconciliation_service.reconcile_all_tables()
            
            assert 'tables' in result
            assert 'overall_match' in result
            assert len(result['tables']) == 3
    
    def test_find_duplicates(self, reconciliation_service):
        """Test duplicate detection."""
        df = pd.DataFrame({
            'id': [1, 2, 2, 3, 3, 3, 4],
            'value': ['a', 'b', 'b', 'c', 'c', 'c', 'd']
        })
        
        duplicates = reconciliation_service._find_duplicates(df, 'id')
        assert len(duplicates) == 2  # IDs 2 and 3 have duplicates
    
    def test_find_duplicates_empty(self, reconciliation_service):
        """Test duplicate detection with empty DataFrame."""
        df = pd.DataFrame()
        duplicates = reconciliation_service._find_duplicates(df, 'id')
        assert duplicates == []
    
    def test_determine_status(self, reconciliation_service):
        """Test status determination logic."""
        assert reconciliation_service._determine_status(99.0) == 'PASS'
        assert reconciliation_service._determine_status(96.0) == 'WARNING'
        assert reconciliation_service._determine_status(85.0) == 'FAIL'
        assert reconciliation_service._determine_status(98.0) == 'PASS'
        assert reconciliation_service._determine_status(90.0) == 'WARNING'