"""
Excel export functionality.
"""
import pandas as pd
from io import BytesIO
from datetime import datetime
import xlsxwriter

from utils.logger import get_logger

logger = get_logger()

class ExportExcel:
    """Export data to Excel format."""
    
    def create_excel_report(self, data: pd.DataFrame, report_type: str) -> BytesIO:
        """Create an Excel report from DataFrame."""
        try:
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Write main data
                data.to_excel(writer, sheet_name='Data', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Data']
                
                # Add formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BD',
                    'border': 1
                })
                
                # Write header with format
                for col_num, value in enumerate(data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Add summary sheet
                summary_data = {
                    'Report Type': [report_type],
                    'Generated Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    'Total Rows': [len(data)],
                    'Total Columns': [len(data.columns)]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Add metadata sheet
                metadata = {
                    'Attribute': ['Application', 'Version', 'Report Type', 'Export Date'],
                    'Value': ['Enterprise Data Reliability Platform', '1.0.0', report_type, datetime.now().isoformat()]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for i, col in enumerate(data.columns):
                        column_width = max(data[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, min(column_width, 50))
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating Excel report: {str(e)}")
            raise