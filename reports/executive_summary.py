"""
Export summary report functionality.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import json

from utils.logger import get_logger
from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.quality_service import QualityService
from services.signoff_service import SignOffService

logger = get_logger()

class ExportSummary:
    """Generate summary reports for export."""
    
    def __init__(self):
        self.completeness_service = CompletenessService()
        self.freshness_service = FreshnessService()
        self.reconciliation_service = ReconciliationService()
        self.quality_service = QualityService()
        self.signoff_service = SignOffService()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        try:
            # Get all metrics
            completeness = self.completeness_service.validate_all_tables()
            freshness = self.freshness_service.validate_all_tables()
            reconciliation = self.reconciliation_service.reconcile_all_tables()
            quality = self.quality_service.calculate_quality_score()
            signoff = self.signoff_service.generate_sign_off()
            
            summary = {
                'report_date': datetime.now().isoformat(),
                'executive_summary': {
                    'quality_score': quality['quality_score'],
                    'quality_tier': quality['quality_tier'],
                    'sign_off_status': signoff['sign_off_status']
                },
                'completeness_summary': {
                    'overall': completeness['overall_completeness'],
                    'tables': {
                        table: {
                            'completeness': data['completeness_percentage'],
                            'missing_records': data['missing_records'],
                            'status': data['status']
                        }
                        for table, data in completeness['tables'].items()
                    }
                },
                'freshness_summary': {
                    'overall': freshness['overall_freshness'],
                    'tables': {
                        table: {
                            'freshness': data['freshness_percentage'],
                            'delay_minutes': data.get('delay_minutes', 0),
                            'status': data['status']
                        }
                        for table, data in freshness['tables'].items()
                    }
                },
                'reconciliation_summary': {
                    'overall': reconciliation['overall_match'],
                    'tables': {
                        table: {
                            'match_percentage': data['match_percentage'],
                            'missing_in_warehouse': data.get('missing_in_warehouse', 0),
                            'extra_in_warehouse': data.get('extra_in_warehouse', 0),
                            'duplicates': data.get('source_duplicates', 0) + data.get('warehouse_duplicates', 0),
                            'status': data['status']
                        }
                        for table, data in reconciliation['tables'].items()
                        if 'match_percentage' in data
                    }
                },
                'quality_components': {
                    component: {
                        'score': data['score'],
                        'weight': data['weight'],
                        'weighted_score': data['weighted_score']
                    }
                    for component, data in quality['components'].items()
                },
                'recommendations': signoff['recommendations']
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def generate_summary_dataframe(self) -> pd.DataFrame:
        """Generate summary as DataFrame for export."""
        summary = self.generate_summary()
        
        # Flatten summary for DataFrame
        flattened_data = []
        
        # Executive summary
        exec_summary = summary['executive_summary']
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Quality Score',
            'Value': exec_summary['quality_score'],
            'Status': exec_summary['quality_tier']
        })
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Sign-off Status',
            'Value': exec_summary['sign_off_status'],
            'Status': exec_summary['sign_off_status']
        })
        
        # Completeness
        comp_summary = summary['completeness_summary']
        flattened_data.append({
            'Category': 'Completeness',
            'Metric': 'Overall',
            'Value': comp_summary['overall'],
            'Status': 'PASS' if comp_summary['overall'] >= 99 else 'WARNING'
        })
        for table, data in comp_summary['tables'].items():
            flattened_data.append({
                'Category': 'Completeness',
                'Metric': f"{table.capitalize()}",
                'Value': data['completeness'],
                'Status': data['status']
            })
        
        # Freshness
        fresh_summary = summary['freshness_summary']
        flattened_data.append({
            'Category': 'Freshness',
            'Metric': 'Overall',
            'Value': fresh_summary['overall'],
            'Status': 'PASS' if fresh_summary['overall'] >= 95 else 'WARNING'
        })
        for table, data in fresh_summary['tables'].items():
            flattened_data.append({
                'Category': 'Freshness',
                'Metric': f"{table.capitalize()} Delay (min)",
                'Value': data['delay_minutes'],
                'Status': data['status']
            })
        
        # Reconciliation
        recon_summary = summary['reconciliation_summary']
        flattened_data.append({
            'Category': 'Reconciliation',
            'Metric': 'Overall',
            'Value': recon_summary['overall'],
            'Status': 'PASS' if recon_summary['overall'] >= 98 else 'WARNING'
        })
        for table, data in recon_summary['tables'].items():
            flattened_data.append({
                'Category': 'Reconciliation',
                'Metric': f"{table.capitalize()} Match %",
                'Value': data['match_percentage'],
                'Status': data['status']
            })
            flattened_data.append({
                'Category': 'Reconciliation',
                'Metric': f"{table.capitalize()} Missing",
                'Value': data['missing_in_warehouse'],
                'Status': 'WARNING' if data['missing_in_warehouse'] > 0 else 'PASS'
            })
        
        # Quality Components
        for component, data in summary['quality_components'].items():
            flattened_data.append({
                'Category': 'Quality Components',
                'Metric': component.replace('_', ' ').title(),
                'Value': data['score'],
                'Status': 'PASS' if data['score'] >= 90 else 'WARNING'
            })
        
        return pd.DataFrame(flattened_data)