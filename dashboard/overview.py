"""
Executive Overview dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from services.completeness_service import CompletenessService
from services.freshness_service import FreshnessService
from services.reconciliation_service import ReconciliationService
from services.pipeline_health import PipelineHealthService
from services.quality_service import QualityService
from services.signoff_service import SignOffService
from utils.logger import get_logger
from utils.charts import create_gauge_chart, create_kpi_card

logger = get_logger()

def render_overview():
    """Render the executive overview dashboard."""
    st.title("🏢 Executive Overview")
    st.caption("Enterprise Data Reliability Dashboard")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Initialize services
    completeness_service = CompletenessService()
    freshness_service = FreshnessService()
    reconciliation_service = ReconciliationService()
    pipeline_service = PipelineHealthService()
    quality_service = QualityService()
    signoff_service = SignOffService()
    
    # Load data with caching
    @st.cache_data(ttl=60)
    def load_metrics():
        try:
            return {
                'completeness': completeness_service.validate_all_tables(),
                'freshness': freshness_service.validate_all_tables(),
                'reconciliation': reconciliation_service.reconcile_all_tables(),
                'pipeline': pipeline_service.get_pipeline_status(),
                'quality': quality_service.calculate_quality_score(),
                'signoff': signoff_service.generate_sign_off()
            }
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")
            return None
    
    metrics = load_metrics()
    
    if not metrics:
        st.error("Failed to load metrics. Please check the application logs.")
        return
    
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Data Reliability Score",
            f"{metrics['quality']['quality_score']:.1f}%",
            delta="Excellent" if metrics['quality']['quality_score'] >= 95 else "Needs Attention"
        )
    
    with col2:
        st.metric(
            "✅ Sign-off Status",
            metrics['signoff']['sign_off_status'],
            delta="Ready" if metrics['signoff']['sign_off_status'] == "PASS" else "Review Required"
        )
    
    with col3:
        pipeline_status = metrics['pipeline'].get('status', 'UNKNOWN')
        st.metric(
            "🔄 Pipeline Health",
            pipeline_status,
            delta="Operational" if pipeline_status == "HEALTHY" else "Issues Detected"
        )
    
    with col4:
        st.metric(
            "📈 Quality Tier",
            metrics['quality']['quality_tier'],
            delta=f"Score: {metrics['quality']['quality_score']:.1f}%"
        )
    
    # Charts section
    st.subheader("📈 Key Metrics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score gauge
        fig_gauge = create_gauge_chart(
            metrics['quality']['quality_score'],
            "Overall Quality Score"
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Component breakdown
        components = metrics['quality']['components']
        df_components = pd.DataFrame({
            'Component': list(components.keys()),
            'Score': [c['score'] for c in components.values()]
        })
        
        fig_bar = px.bar(
            df_components,
            x='Component',
            y='Score',
            title='Quality Component Scores',
            color='Score',
            color_continuous_scale='RdYlGn',
            range_y=[0, 100]
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Pipeline status
    st.subheader("🔄 Pipeline Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Runs",
            metrics['pipeline'].get('total_runs', 0)
        )
    
    with col2:
        st.metric(
            "Success Rate",
            f"{metrics['pipeline'].get('success_rate', 0):.1f}%",
            delta="✅" if metrics['pipeline'].get('success_rate', 0) >= 95 else "⚠️"
        )
    
    with col3:
        st.metric(
            "Failed Runs",
            metrics['pipeline'].get('failed_runs', 0)
        )
    
    with col4:
        st.metric(
            "Delayed Runs",
            metrics['pipeline'].get('delayed_runs', 0)
        )
    
    # Recent sign-off details
    st.subheader("📋 Recent Sign-off Details")
    
    if metrics['signoff']:
        signoff = metrics['signoff']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Status:** {signoff['sign_off_status']}")
            st.info(f"**Quality Score:** {signoff['quality_score']:.1f}%")
            st.info(f"**Quality Tier:** {signoff['quality_tier']}")
        
        with col2:
            st.info(f"**Freshness:** {signoff['freshness_score']:.1f}%")
            st.info(f"**Completeness:** {signoff['completeness_score']:.1f}%")
            st.info(f"**Reconciliation:** {signoff['reconciliation_score']:.1f}%")
        
        # Recommendations
        st.warning("**Recommendations**")
        for rec in signoff['recommendations']:
            st.write(f"• {rec}")
    
    # Last refresh timestamp
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")