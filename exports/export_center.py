"""
Export Center dashboard page.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from services.metrics_service import MetricsService
from reports.export_excel import ExportExcel
from utils.logger import get_logger

logger = get_logger()

def render_export_center():
    """Render the export center dashboard."""
    st.title("📤 Export Center")
    st.caption("Export reports and data in multiple formats")
    
    # Initialize services
    metrics_service = MetricsService()
    
    # Export options
    st.subheader("📊 Select Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_type = st.selectbox(
            "Export Type",
            ["Dashboard Data", "Completeness Report", "Freshness Report", 
             "Reconciliation Report", "Quality Report", "Audit Logs"]
        )
    
    with col2:
        format_type = st.selectbox(
            "Export Format",
            ["CSV", "Excel", "PDF"]
        )
    
    # Load data based on selection
    @st.cache_data(ttl=60)
    def load_export_data(export_type):
        if export_type == "Dashboard Data":
            return metrics_service.get_all_metrics()
        elif export_type == "Completeness Report":
            from services.completeness_service import CompletenessService
            service = CompletenessService()
            return service.validate_all_tables()
        elif export_type == "Freshness Report":
            from services.freshness_service import FreshnessService
            service = FreshnessService()
            return service.validate_all_tables()
        elif export_type == "Reconciliation Report":
            from services.reconciliation_service import ReconciliationService
            service = ReconciliationService()
            return service.reconcile_all_tables()
        elif export_type == "Quality Report":
            from services.quality_service import QualityService
            service = QualityService()
            return service.calculate_quality_score()
        elif export_type == "Audit Logs":
            return metrics_service.get_audit_logs(limit=1000)
        else:
            return {}
    
    data = load_export_data(export_type)
    
    # Display preview
    if isinstance(data, dict):
        df = pd.DataFrame([data]) if data else pd.DataFrame()
        if df.empty:
            st.warning("No data available for export")
        else:
            st.dataframe(df, use_container_width=True)
            st.info(f"Data contains {len(df)} rows and {len(df.columns)} columns")
            
    elif isinstance(data, pd.DataFrame):
        if data.empty:
            st.warning("No data available for export")
        else:
            st.dataframe(data, use_container_width=True)
            st.info(f"Data contains {len(data)} rows and {len(data.columns)} columns")
    else:
        st.warning("No data available for export")
    
    # Export button
    if st.button("📤 Export Data", use_container_width=True, type="primary"):
        try:
            if isinstance(data, dict):
                export_df = pd.DataFrame([data])
            elif isinstance(data, pd.DataFrame):
                export_df = data
            else:
                st.error("Unsupported data format for export")
                return
            
            if format_type == "CSV":
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{export_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            elif format_type == "Excel":
                excel_exporter = ExportExcel()
                excel_data = excel_exporter.create_excel_report(export_df, export_type)
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"{export_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif format_type == "PDF":
                st.info("PDF export is available in the professional version.")
            
            st.success("Export ready for download!")
        except Exception as e:
            st.error(f"Error during export: {str(e)}")