"""
PDF export functionality.
"""
import pandas as pd
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger()

class ExportPDF:
    """Export data to PDF format."""
    
    def __init__(self):
        self.html_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 10px; }
                h2 { color: #2c3e50; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th { background-color: #1f77b4; color: white; padding: 12px; text-align: left; }
                td { padding: 10px; border-bottom: 1px solid #ddd; }
                tr:hover { background-color: #f5f5f5; }
                .header { text-align: center; margin-bottom: 30px; }
                .date { color: #7f8c8d; font-size: 14px; }
                .status-pass { color: #27ae60; font-weight: bold; }
                .status-warning { color: #f39c12; font-weight: bold; }
                .status-fail { color: #e74c3c; font-weight: bold; }
                .summary-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .metric-value { font-size: 24px; font-weight: bold; }
                .metric-label { color: #7f8c8d; }
                .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
                .card { background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
    
    def create_pdf_report(self, data: pd.DataFrame, report_type: str) -> BytesIO:
        """Create a PDF report from DataFrame."""
        try:
            # Generate HTML content
            html_content = self._generate_html_content(data, report_type)
            
            # Create PDF using weasyprint or reportlab
            # For now, return HTML as fallback
            output = BytesIO()
            output.write(html_content.encode('utf-8'))
            output.seek(0)
            
            return output
            
        except Exception as e:
            logger.error(f"Error creating PDF report: {str(e)}")
            raise
    
    def _generate_html_content(self, data: pd.DataFrame, report_type: str) -> str:
        """Generate HTML content for PDF."""
        # Header
        html = f"""
        <div class="header">
            <h1>Enterprise Data Reliability Platform</h1>
            <h2>{report_type}</h2>
            <div class="date">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        """
        
        # Summary metrics
        html += self._generate_summary_metrics(data)
        
        # Data table
        html += self._generate_data_table(data)
        
        return self.html_template.format(content=html)
    
    def _generate_summary_metrics(self, data: pd.DataFrame) -> str:
        """Generate summary metrics section."""
        html = '<div class="grid">'
        
        # Calculate summary metrics
        total_rows = len(data)
        pass_count = len(data[data['Status'] == 'PASS']) if 'Status' in data.columns else 0
        warning_count = len(data[data['Status'] == 'WARNING']) if 'Status' in data.columns else 0
        fail_count = len(data[data['Status'] == 'FAIL']) if 'Status' in data.columns else 0
        
        html += f"""
        <div class="card">
            <div class="metric-label">Total Metrics</div>
            <div class="metric-value">{total_rows}</div>
        </div>
        <div class="card">
            <div class="metric-label">PASS</div>
            <div class="metric-value" style="color: #27ae60;">{pass_count}</div>
        </div>
        <div class="card">
            <div class="metric-label">WARNING / FAIL</div>
            <div class="metric-value" style="color: #e74c3c;">{warning_count + fail_count}</div>
        </div>
        """
        
        html += '</div>'
        return html
    
    def _generate_data_table(self, data: pd.DataFrame) -> str:
        """Generate data table section."""
        if data.empty:
            return '<p>No data available for this report.</p>'
        
        html = '<h2>Detailed Metrics</h2>'
        html += '<table>'
        
        # Header
        html += '<tr>'
        for col in data.columns:
            html += f'<th>{col}</th>'
        html += '</tr>'
        
        # Rows
        for _, row in data.iterrows():
            html += '<tr>'
            for col in data.columns:
                value = row[col]
                if col == 'Status':
                    status_class = f"status-{str(value).lower()}"
                    html += f'<td class="{status_class}">{value}</td>'
                else:
                    html += f'<td>{value}</td>'
            html += '</tr>'
        
        html += '</table>'
        return html