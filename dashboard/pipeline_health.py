"""
Pipeline Health dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from services.pipeline_health import PipelineHealthService
from utils.logger import get_logger

logger = get_logger()

def render_pipeline_health():
    """Render the pipeline health dashboard."""
    st.title("🔄 Pipeline Health Monitoring")
    st.caption("Monitor pipeline execution health and performance")
    
    # Initialize service
    pipeline_service = PipelineHealthService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_pipeline_data():
        return pipeline_service.get_pipeline_status()
    
    data = load_pipeline_data()
    
    if 'error' in data:
        st.error(f"Error loading pipeline data: {data['error']}")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Runs (24h)",
            data.get('total_runs', 0),
            delta="Active"
        )
    
    with col2:
        st.metric(
            "Success Rate",
            f"{data.get('success_rate', 0):.1f}%",
            delta="✅" if data.get('success_rate', 0) >= 95 else "⚠️"
        )
    
    with col3:
        st.metric(
            "Failed Runs",
            data.get('failed_runs', 0),
            delta="❌" if data.get('failed_runs', 0) > 0 else "✅"
        )
    
    with col4:
        st.metric(
            "Delayed Runs",
            data.get('delayed_runs', 0),
            delta="⏰" if data.get('delayed_runs', 0) > 0 else "✅"
        )
    
    # Pipeline status cards
    st.subheader("📊 Pipeline Status Overview")
    
    # Get pipeline details for each pipeline
    pipelines = ['order_pipeline', 'customer_pipeline', 'event_pipeline', 
                'reconciliation_pipeline', 'quality_pipeline']
    
    cols = st.columns(5)
    
    for i, pipeline in enumerate(pipelines):
        with cols[i]:
            details = pipeline_service.get_pipeline_details(pipeline)
            status = details.get('status', 'UNKNOWN') if 'error' not in details else 'UNKNOWN'
            
            color = {
                'HEALTHY': '🟢',
                'WARNING': '🟡',
                'CRITICAL': '🔴',
                'FAILED': '🔴',
                'UNKNOWN': '⚪'
            }.get(status, '⚪')
            
            st.metric(
                f"{color} {pipeline.replace('_', ' ').title()}",
                status,
                delta=f"{details.get('success_rate', 0):.1f}% success" if 'error' not in details else "No data"
            )
    
    # Pipeline performance charts
    st.subheader("📈 Pipeline Performance")
    
    # Get detailed pipeline history
    pipeline_health = []
    for pipeline in pipelines:
        details = pipeline_service.get_pipeline_details(pipeline)
        if 'error' not in details:
            pipeline_health.append({
                'Pipeline': pipeline.replace('_', ' ').title(),
                'Success Rate %': details.get('success_rate', 0),
                'Total Runs': details.get('total_runs', 0),
                'Failed': details.get('failed', 0),
                'Status': details.get('status', 'UNKNOWN')
            })
    
    if pipeline_health:
        df_health = pd.DataFrame(pipeline_health)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate bar chart
            fig_success = px.bar(
                df_health,
                x='Pipeline',
                y='Success Rate %',
                title='Success Rate by Pipeline',
                color='Success Rate %',
                color_continuous_scale='RdYlGn',
                range_y=[0, 100],
                text='Success Rate %'
            )
            fig_success.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_success.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_success, use_container_width=True)
        
        with col2:
            # Pipeline statistics
            fig_stats = go.Figure()
            
            fig_stats.add_trace(go.Bar(
                name='Success',
                x=df_health['Pipeline'],
                y=df_health['Total Runs'] - df_health['Failed'],
                marker_color='green'
            ))
            
            fig_stats.add_trace(go.Bar(
                name='Failed',
                x=df_health['Pipeline'],
                y=df_health['Failed'],
                marker_color='red'
            ))
            
            fig_stats.update_layout(
                title='Run Success vs Failure by Pipeline',
                barmode='stack',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_stats, use_container_width=True)
    
    # Validation timestamp
    st.caption(f"Last updated: {data.get('validation_timestamp', datetime.now().isoformat())}")