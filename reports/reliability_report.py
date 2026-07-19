"""
Reliability report generation.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import json

from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.quality_service import QualityService
from services.signoff_service import SignOffService
from services.pipeline_health import PipelineHealthService
from reports.export_summary import ExportSummary
from utils.logger import get_logger

logger = get_logger()

class ReliabilityReport:
    """Generate comprehensive reliability reports."""
    
    def __init__(self):
        self.completeness_service = CompletenessService()
        self.freshness_service = FreshnessService()
        self.reconciliation_service = ReconciliationService()
        self.quality_service = QualityService()
        self.signoff_service = SignOffService()
        self.pipeline_service = PipelineHealthService()
        self.export_summary = ExportSummary()
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate full reliability report."""
        try:
            # Get all metrics
            completeness = self.completeness_service.validate_all_tables()
            freshness = self.freshness_service.validate_all_tables()
            reconciliation = self.reconciliation_service.reconcile_all_tables()
            quality = self.quality_service.calculate_quality_score()
            signoff = self.signoff_service.generate_sign_off()
            pipeline = self.pipeline_service.get_pipeline_status()
            
            report = {
                'report_metadata': {
                    'report_id': f"REL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    'generated_at': datetime.now().isoformat(),
                    'report_version': '1.0',
                    'generated_by': 'Enterprise Data Reliability Platform'
                },
                'executive_summary': {
                    'overall_quality_score': quality['quality_score'],
                    'quality_tier': quality['quality_tier'],
                    'sign_off_status': signoff['sign_off_status'],
                    'pipeline_health': pipeline.get('status', 'UNKNOWN'),
                    'critical_issues_count': self._count_critical_issues(quality, pipeline)
                },
                'completeness_report': {
                    'overall': completeness['overall_completeness'],
                    'tables': completeness['tables']
                },
                'freshness_report': {
                    'overall': freshness['overall_freshness'],
                    'tables': freshness['tables']
                },
                'reconciliation_report': {
                    'overall': reconciliation['overall_match'],
                    'tables': reconciliation['tables']
                },
                'quality_components': quality['components'],
                'pipeline_health': pipeline,
                'recommendations': signoff['recommendations'],
                'timestamp': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating full report: {str(e)}")
            raise
    
    def _count_critical_issues(self, quality: Dict, pipeline: Dict) -> int:
        """Count critical issues in the report."""
        critical_issues = 0
        
        # Check quality score
        if quality['quality_score'] < 85:
            critical_issues += 1
        
        # Check pipeline health
        if pipeline.get('status') == 'CRITICAL':
            critical_issues += 1
        
        # Check quality components
        for comp in quality['components'].values():
            if comp['score'] < 80:
                critical_issues += 1
                break
        
        return critical_issues
    
    def generate_report_dataframe(self) -> pd.DataFrame:
        """Generate report as DataFrame for export."""
        report = self.generate_full_report()
        
        # Flatten report for DataFrame
        flattened_data = []
        
        # Executive summary
        exec_summary = report['executive_summary']
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Quality Score',
            'Value': exec_summary['overall_quality_score'],
            'Status': exec_summary['quality_tier'],
            'Timestamp': report['timestamp']
        })
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Sign-off Status',
            'Value': exec_summary['sign_off_status'],
            'Status': exec_summary['sign_off_status'],
            'Timestamp': report['timestamp']
        })
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Pipeline Health',
            'Value': exec_summary['pipeline_health'],
            'Status': exec_summary['pipeline_health'],
            'Timestamp': report['timestamp']
        })
        flattened_data.append({
            'Category': 'Executive Summary',
            'Metric': 'Critical Issues',
            'Value': exec_summary['critical_issues_count'],
            'Status': 'WARNING' if exec_summary['critical_issues_count'] > 0 else 'PASS',
            'Timestamp': report['timestamp']
        })
        
        # Completeness
        comp_report = report['completeness_report']
        flattened_data.append({
            'Category': 'Completeness',
            'Metric': 'Overall',
            'Value': comp_report['overall'],
            'Status': 'PASS' if comp_report['overall'] >= 99 else 'WARNING',
            'Timestamp': report['timestamp']
        })
        for table, data in comp_report['tables'].items():
            flattened_data.append({
                'Category': f'Completeness - {table.capitalize()}',
                'Metric': 'Completeness %',
                'Value': data['completeness_percentage'],
                'Status': data['status'],
                'Timestamp': report['timestamp']
            })
            flattened_data.append({
                'Category': f'Completeness - {table.capitalize()}',
                'Metric': 'Missing Records',
                'Value': data['missing_records'],
                'Status': 'WARNING' if data['missing_records'] > 0 else 'PASS',
                'Timestamp': report['timestamp']
            })
        
        # Freshness
        fresh_report = report['freshness_report']
        flattened_data.append({
            'Category': 'Freshness',
            'Metric': 'Overall',
            'Value': fresh_report['overall'],
            'Status': 'PASS' if fresh_report['overall'] >= 95 else 'WARNING',
            'Timestamp': report['timestamp']
        })
        for table, data in fresh_report['tables'].items():
            flattened_data.append({
                'Category': f'Freshness - {table.capitalize()}',
                'Metric': 'Freshness %',
                'Value': data['freshness_percentage'],
                'Status': data['status'],
                'Timestamp': report['timestamp']
            })
            if data.get('delay_minutes'):
                flattened_data.append({
                    'Category': f'Freshness - {table.capitalize()}',
                    'Metric': 'Delay (minutes)',
                    'Value': data['delay_minutes'],
                    'Status': 'WARNING' if data['delay_minutes'] > 60 else 'PASS',
                    'Timestamp': report['timestamp']
                })
        
        # Reconciliation
        recon_report = report['reconciliation_report']
        flattened_data.append({
            'Category': 'Reconciliation',
            'Metric': 'Overall Match %',
            'Value': recon_report['overall'],
            'Status': 'PASS' if recon_report['overall'] >= 98 else 'WARNING',
            'Timestamp': report['timestamp']
        })
        for table, data in recon_report['tables'].items():
            if 'match_percentage' in data:
                flattened_data.append({
                    'Category': f'Reconciliation - {table.capitalize()}',
                    'Metric': 'Match %',
                    'Value': data['match_percentage'],
                    'Status': data['status'],
                    'Timestamp': report['timestamp']
                })
                flattened_data.append({
                    'Category': f'Reconciliation - {table.capitalize()}',
                    'Metric': 'Missing in Warehouse',
                    'Value': data.get('missing_in_warehouse', 0),
                    'Status': 'WARNING' if data.get('missing_in_warehouse', 0) > 0 else 'PASS',
                    'Timestamp': report['timestamp']
                })
        
        # Quality Components
        for component, data in report['quality_components'].items():
            flattened_data.append({
                'Category': 'Quality Components',
                'Metric': component.replace('_', ' ').title(),
                'Value': data['score'],
                'Status': 'PASS' if data['score'] >= 90 else 'WARNING',
                'Timestamp': report['timestamp']
            })
        
        # Pipeline
        pipeline_report = report['pipeline_health']
        if 'error' not in pipeline_report:
            flattened_data.append({
                'Category': 'Pipeline Health',
                'Metric': 'Success Rate',
                'Value': pipeline_report.get('success_rate', 0),
                'Status': pipeline_report.get('status', 'UNKNOWN'),
                'Timestamp': report['timestamp']
            })
            flattened_data.append({
                'Category': 'Pipeline Health',
                'Metric': 'Failed Runs',
                'Value': pipeline_report.get('failed_runs', 0),
                'Status': 'WARNING' if pipeline_report.get('failed_runs', 0) > 0 else 'PASS',
                'Timestamp': report['timestamp']
            })
        
        return pd.DataFrame(flattened_data)
    
    def generate_summary_text(self) -> str:
        """Generate human-readable summary text."""
        report = self.generate_full_report()
        
        summary_lines = []
        summary_lines.append("=" * 60)
        summary_lines.append("DATA RELIABILITY REPORT")
        summary_lines.append("=" * 60)
        summary_lines.append(f"Generated: {report['timestamp']}")
        summary_lines.append("")
        
        # Executive Summary
        exec_summary = report['executive_summary']
        summary_lines.append("EXECUTIVE SUMMARY")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Quality Score: {exec_summary['overall_quality_score']:.1f}% ({exec_summary['quality_tier']})")
        summary_lines.append(f"Sign-off Status: {exec_summary['sign_off_status']}")
        summary_lines.append(f"Pipeline Health: {exec_summary['pipeline_health']}")
        summary_lines.append(f"Critical Issues: {exec_summary['critical_issues_count']}")
        summary_lines.append("")
        
        # Completeness
        comp_report = report['completeness_report']
        summary_lines.append("COMPLETENESS")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Overall: {comp_report['overall']:.1f}%")
        for table, data in comp_report['tables'].items():
            summary_lines.append(f"  {table.capitalize()}: {data['completeness_percentage']:.1f}% ({data['status']})")
        summary_lines.append("")
        
        # Freshness
        fresh_report = report['freshness_report']
        summary_lines.append("FRESHNESS")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Overall: {fresh_report['overall']:.1f}%")
        for table, data in fresh_report['tables'].items():
            delay = data.get('delay_minutes', 0)
            summary_lines.append(f"  {table.capitalize()}: {data['freshness_percentage']:.1f}% (Delay: {delay:.1f} min)")
        summary_lines.append("")
        
        # Reconciliation
        recon_report = report['reconciliation_report']
        summary_lines.append("RECONCILIATION")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Overall: {recon_report['overall']:.1f}%")
        for table, data in recon_report['tables'].items():
            if 'match_percentage' in data:
                summary_lines.append(f"  {table.capitalize()}: {data['match_percentage']:.1f}% ({data['status']})")
        summary_lines.append("")
        
        # Recommendations
        summary_lines.append("RECOMMENDATIONS")
        summary_lines.append("-" * 30)
        for rec in report['recommendations']:
            summary_lines.append(f"• {rec}")
        summary_lines.append("")
        
        summary_lines.append("=" * 60)
        summary_lines.append("END OF REPORT")
        summary_lines.append("=" * 60)
        
        return "\n".join(summary_lines)