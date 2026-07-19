"""
Unit tests for sign-off service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from services.signoff_service import SignOffService

class TestSignOffService:
    """Test sign-off service functionality."""
    
    @pytest.fixture
    def signoff_service(self):
        """Create sign-off service instance."""
        return SignOffService()
    
    @patch('services.signoff_service.QualityService')
    @patch('services.signoff_service.PipelineHealthService')
    @patch('services.signoff_service.CompletenessService')
    @patch('services.signoff_service.FreshnessService')
    @patch('services.signoff_service.ReconciliationService')
    def test_generate_sign_off_pass(self, mock_recon, mock_fresh, mock_comp, 
                                   mock_pipeline, mock_quality, signoff_service):
        """Test sign-off generation with PASS status."""
        # Mock services
        mock_quality.return_value.calculate_quality_score.return_value = {
            'quality_score': 98.5,
            'quality_tier': 'EXCELLENT',
            'components': {}
        }
        
        mock_pipeline.return_value.get_pipeline_status.return_value = {
            'status': 'HEALTHY',
            'success_rate': 97.0
        }
        
        mock_comp.return_value.validate_all_tables.return_value = {
            'overall_completeness': 99.5,
            'tables': {}
        }
        
        mock_fresh.return_value.validate_all_tables.return_value = {
            'overall_freshness': 96.0,
            'tables': {}
        }
        
        mock_recon.return_value.reconcile_all_tables.return_value = {
            'overall_match': 98.5,
            'tables': {}
        }
        
        result = signoff_service.generate_sign_off()
        
        assert result['sign_off_status'] == 'PASS'
        assert result['quality_score'] == 98.5
        assert result['quality_tier'] == 'EXCELLENT'
        assert result['pipeline_health'] == 'HEALTHY'
        assert 'recommendations' in result
    
    @patch('services.signoff_service.QualityService')
    @patch('services.signoff_service.PipelineHealthService')
    @patch('services.signoff_service.CompletenessService')
    @patch('services.signoff_service.FreshnessService')
    @patch('services.signoff_service.ReconciliationService')
    def test_generate_sign_off_warning(self, mock_recon, mock_fresh, mock_comp, 
                                      mock_pipeline, mock_quality, signoff_service):
        """Test sign-off generation with WARNING status."""
        mock_quality.return_value.calculate_quality_score.return_value = {
            'quality_score': 92.0,
            'quality_tier': 'GOOD',
            'components': {}
        }
        
        mock_pipeline.return_value.get_pipeline_status.return_value = {
            'status': 'WARNING',
            'success_rate': 88.0
        }
        
        mock_comp.return_value.validate_all_tables.return_value = {
            'overall_completeness': 96.0,
            'tables': {}
        }
        
        mock_fresh.return_value.validate_all_tables.return_value = {
            'overall_freshness': 90.0,
            'tables': {}
        }
        
        mock_recon.return_value.reconcile_all_tables.return_value = {
            'overall_match': 94.0,
            'tables': {}
        }
        
        result = signoff_service.generate_sign_off()
        
        assert result['sign_off_status'] == 'WARNING'
        assert result['quality_score'] == 92.0
        assert result['quality_tier'] == 'GOOD'
    
    @patch('services.signoff_service.QualityService')
    @patch('services.signoff_service.PipelineHealthService')
    @patch('services.signoff_service.CompletenessService')
    @patch('services.signoff_service.FreshnessService')
    @patch('services.signoff_service.ReconciliationService')
    def test_generate_sign_off_fail(self, mock_recon, mock_fresh, mock_comp, 
                                   mock_pipeline, mock_quality, signoff_service):
        """Test sign-off generation with FAIL status."""
        mock_quality.return_value.calculate_quality_score.return_value = {
            'quality_score': 75.0,
            'quality_tier': 'POOR',
            'components': {}
        }
        
        mock_pipeline.return_value.get_pipeline_status.return_value = {
            'status': 'CRITICAL',
            'success_rate': 65.0
        }
        
        mock_comp.return_value.validate_all_tables.return_value = {
            'overall_completeness': 85.0,
            'tables': {}
        }
        
        mock_fresh.return_value.validate_all_tables.return_value = {
            'overall_freshness': 70.0,
            'tables': {}
        }
        
        mock_recon.return_value.reconcile_all_tables.return_value = {
            'overall_match': 80.0,
            'tables': {}
        }
        
        result = signoff_service.generate_sign_off()
        
        assert result['sign_off_status'] == 'FAIL'
        assert result['quality_score'] == 75.0
        assert result['quality_tier'] == 'POOR'
        assert 'URGENT' in result['recommendations'][0]
    
    def test_evaluate_sign_off(self, signoff_service):
        """Test sign-off evaluation logic."""
        # PASS conditions
        assert signoff_service._evaluate_sign_off(98.5, 96.0, 99.5, 97.0) == 'PASS'
        assert signoff_service._evaluate_sign_off(99.0, 97.0, 99.5, 98.0) == 'PASS'
        
        # WARNING conditions
        assert signoff_service._evaluate_sign_off(93.0, 90.0, 95.0, 88.0) == 'WARNING'
        assert signoff_service._evaluate_sign_off(92.0, 88.0, 94.0, 90.0) == 'WARNING'
        
        # FAIL conditions
        assert signoff_service._evaluate_sign_off(85.0, 80.0, 88.0, 75.0) == 'FAIL'
        assert signoff_service._evaluate_sign_off(70.0, 65.0, 80.0, 60.0) == 'FAIL'
    
    def test_get_quality_tier(self, signoff_service):
        """Test quality tier determination."""
        assert signoff_service._get_quality_tier(97.0) == 'EXCELLENT'
        assert signoff_service._get_quality_tier(90.0) == 'GOOD'
        assert signoff_service._get_quality_tier(80.0) == 'FAIR'
        assert signoff_service._get_quality_tier(70.0) == 'POOR'
        assert signoff_service._get_quality_tier(95.0) == 'EXCELLENT'
        assert signoff_service._get_quality_tier(85.0) == 'GOOD'
        assert signoff_service._get_quality_tier(75.0) == 'FAIR'
    
    def test_get_recommendations_pass(self, signoff_service):
        """Test recommendations for PASS status."""
        recommendations = signoff_service._get_recommendations(
            'PASS', {'quality_score': 98.0}, {'success_rate': 96.0}
        )
        assert 'All data quality metrics are within acceptable ranges' in recommendations[0]
        assert 'Maintain current monitoring' in recommendations[1]
    
    def test_get_recommendations_warning(self, signoff_service):
        """Test recommendations for WARNING status."""
        recommendations = signoff_service._get_recommendations(
            'WARNING', {'quality_score': 92.0}, {'success_rate': 88.0}
        )
        assert 'Address minor quality issues' in recommendations[0]
    
    def test_get_recommendations_fail(self, signoff_service):
        """Test recommendations for FAIL status."""
        recommendations = signoff_service._get_recommendations(
            'FAIL', {'quality_score': 75.0}, {'success_rate': 65.0}
        )
        assert 'URGENT' in recommendations[0]
        assert 'Review and fix' in recommendations[1] or 'Investigate pipeline' in recommendations[1]