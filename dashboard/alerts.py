"""
Alerts dashboard page.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from services.alert_service import AlertService
from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.pipeline_health import PipelineHealthService
from services.quality_service import QualityService
from utils.logger import get_logger
from config.constants import AlertSeverity

logger = get_logger()

def render_alerts():
    """Render the alerts dashboard."""
    st.title("⚠️ Alerts")
    st.caption("Real-time alerts for data reliability issues")
    
    # Initialize services
    alert_service = AlertService()
    completeness_service = CompletenessService()
    freshness_service = FreshnessService()
    reconciliation_service = ReconciliationService()
    pipeline_service = PipelineHealthService()
    quality_service = QualityService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_metrics_for_alerts():
        try:
            metrics = {
                'completeness': completeness_service.validate_all_tables(),
                'freshness': freshness_service.validate_all_tables(),
                'reconciliation': reconciliation_service.reconcile_all_tables(),
                'pipeline': pipeline_service.get_pipeline_status(),
                'quality': quality_service.calculate_quality_score()
            }
            return alert_service.generate_all_alerts(metrics)
        except Exception as e:
            logger.error(f"Error loading metrics for alerts: {str(e)}")
            return []
    
    alerts = load_metrics_for_alerts()
    
    # Summary metrics
    critical_alerts = sum(1 for a in alerts if a['severity'] == AlertSeverity.CRITICAL.value)
    warning_alerts = sum(1 for a in alerts if a['severity'] == AlertSeverity.WARNING.value)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Alerts",
            len(alerts),
            delta="Active"
        )
    
    with col2:
        st.metric(
            "Critical Alerts",
            critical_alerts,
            delta="🚨" if critical_alerts > 0 else "✅"
        )
    
    with col3:
        st.metric(
            "Warning Alerts",
            warning_alerts,
            delta="⚠️" if warning_alerts > 0 else "✅"
        )
    
    # Filter alerts
    st.subheader("🔍 Filter Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            options=[AlertSeverity.CRITICAL.value, AlertSeverity.WARNING.value],
            default=[AlertSeverity.CRITICAL.value, AlertSeverity.WARNING.value]
        )
    
    with col2:
        type_filter = st.multiselect(
            "Alert Type",
            options=list(set(a['type'] for a in alerts)) if alerts else [],
            default=list(set(a['type'] for a in alerts)) if alerts else []
        )
    
    # Apply filters
    filtered_alerts = [
        a for a in alerts 
        if a['severity'] in severity_filter and a['type'] in type_filter
    ]
    
    # Display alerts
    st.subheader("📋 Alert List")
    
    if not filtered_alerts:
        st.success("✅ No alerts found. All systems are operational!")
    else:
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for alert in filtered_alerts[:20]:  # Show latest 20
            severity = alert['severity']
            alert_type = alert['type']
            message = alert['message']
            timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            if severity == AlertSeverity.CRITICAL.value:
                st.error(f"🚨 **{timestamp}** - {message}")
            else:
                st.warning(f"⚠️ **{timestamp}** - {message}")
            
            # Show details in expander
            with st.expander("View Details"):
                st.json({
                    'Type': alert_type,
                    'Table': alert.get('table', 'N/A'),
                    'Value': alert.get('value', 'N/A'),
                    'Threshold': alert.get('threshold', 'N/A'),
                    'Severity': severity,
                    'Timestamp': timestamp
                })
    
    # Alert statistics
    if alerts:
        st.subheader("📊 Alert Statistics")
        
        # Create alert type distribution
        alert_types = [a['type'] for a in alerts]
        type_counts = pd.Series(alert_types).value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        
        fig_type = px.bar(
            type_counts,
            x='Type',
            y='Count',
            title='Alert Distribution by Type'
        )
        fig_type.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        st.plotly_chart(fig_type, use_container_width=True)
        
        # Alert timeline
        alert_timeline = pd.DataFrame([
            {'Timestamp': pd.to_datetime(a['timestamp']), 'Severity': a['severity']} 
            for a in alerts
        ])
        
        severity_colors = {
            AlertSeverity.CRITICAL.value: 'red',
            AlertSeverity.WARNING.value: 'orange'
        }
        
        fig_timeline = px.scatter(
            alert_timeline,
            x='Timestamp',
            y='Severity',
            title='Alert Timeline',
            color='Severity',
            color_discrete_map=severity_colors
        )
        fig_timeline.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Refresh timestamp
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")