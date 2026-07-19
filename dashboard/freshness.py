"""
Data Freshness dashboard page.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from services.freshness_service import FreshnessService
from utils.logger import get_logger
from utils.charts import create_timeline_chart

logger = get_logger()

def render_freshness():
    """Render the data freshness dashboard."""
    st.title("⏰ Data Freshness Validation")
    st.caption("Monitor data freshness and latency across all tables")
    
    # Initialize service
    freshness_service = FreshnessService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_freshness():
        return freshness_service.validate_all_tables()
    
    data = load_freshness()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Freshness",
            f"{data['overall_freshness']:.1f}%",
            delta="✅" if data['overall_freshness'] >= 95 else "⚠️"
        )
    
    with col2:
        avg_delay = sum(t.get('delay_minutes', 0) for t in data['tables'].values()) / len(data['tables'])
        st.metric(
            "Average Delay",
            f"{avg_delay:.1f} min",
            delta=f"{'🔄' if avg_delay < 30 else '⚠️'}"
        )
    
    with col3:
        freshest_table = max(data['tables'].items(), key=lambda x: x[1]['freshness_percentage'])
        st.metric(
            "Freshest Table",
            freshest_table[0].capitalize(),
            delta=f"{freshest_table[1]['freshness_percentage']:.1f}%"
        )
    
    # Freshness by table
    st.subheader("📋 Freshness by Table")
    
    tables_data = []
    for table_name, table_data in data['tables'].items():
        delay = table_data.get('delay_minutes', 0)
        tables_data.append({
            'Table': table_name.capitalize(),
            'Freshness %': table_data['freshness_percentage'],
            'Delay (min)': delay,
            'Delay (hours)': delay / 60 if delay else 0,
            'Source Latest': table_data.get('source_latest', 'N/A'),
            'Warehouse Latest': table_data.get('warehouse_latest', 'N/A'),
            'Status': table_data['status']
        })
    
    df_tables = pd.DataFrame(tables_data)
    
    # Bar chart for freshness
    fig = px.bar(
        df_tables,
        x='Table',
        y='Freshness %',
        title='Freshness Percentage by Table',
        color='Freshness %',
        color_continuous_scale='RdYlGn',
        range_y=[0, 100],
        text='Freshness %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Delay analysis
    st.subheader("⏱️ Delay Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delay by table
        fig_delay = px.bar(
            df_tables,
            x='Table',
            y='Delay (min)',
            title='Delay by Table (Minutes)',
            color='Delay (min)',
            color_continuous_scale='Viridis'
        )
        fig_delay.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig_delay, use_container_width=True)
    
    with col2:
        # Freshness gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data['overall_freshness'],
            title={'text': "Overall Freshness"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen" if data['overall_freshness'] >= 95 else "orange"},
                'steps': [
                    {'range': [0, 70], 'color': "red"},
                    {'range': [70, 85], 'color': "orange"},
                    {'range': [85, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_gauge.update_layout(height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Validation timestamp
    st.caption(f"Last validated: {data['validation_timestamp']}")