"""
Data Completeness dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from services.completeness_service import CompletenessService
from utils.logger import get_logger
from utils.charts import create_metric_card

logger = get_logger()

def render_completeness():
    """Render the data completeness dashboard."""
    st.title("📊 Data Completeness Validation")
    st.caption("Monitor data completeness across all tables")
    
    # Initialize service
    completeness_service = CompletenessService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_completeness():
        return completeness_service.validate_all_tables()
    
    data = load_completeness()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Completeness",
            f"{data['overall_completeness']:.1f}%",
            delta="✅" if data['overall_completeness'] >= 99 else "⚠️"
        )
    
    with col2:
        table_count = len(data['tables'])
        st.metric(
            "Tables Validated",
            table_count,
            delta="✅ Validated" if table_count > 0 else "No tables"
        )
    
    with col3:
        missing_total = sum(t['missing_records'] for t in data['tables'].values())
        st.metric(
            "Total Missing Records",
            missing_total,
            delta=f"{'⚠️' if missing_total > 0 else '✅'}"
        )
    
    # Completeness by table
    st.subheader("📋 Completeness by Table")
    
    tables_data = []
    for table_name, table_data in data['tables'].items():
        tables_data.append({
            'Table': table_name.capitalize(),
            'Completeness %': table_data['completeness_percentage'],
            'Source Count': table_data['source_count'],
            'Warehouse Count': table_data['warehouse_count'],
            'Missing Records': table_data['missing_records'],
            'Status': table_data['status']
        })
    
    df_tables = pd.DataFrame(tables_data)
    
    # Bar chart
    fig = px.bar(
        df_tables,
        x='Table',
        y='Completeness %',
        title='Completeness Percentage by Table',
        color='Completeness %',
        color_continuous_scale='RdYlGn',
        range_y=[0, 100],
        text='Completeness %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table view
    st.subheader("🔍 Detailed Completeness Report")
    
    # Create detailed table
    detailed_data = []
    for table_name, table_data in data['tables'].items():
        detailed_data.append({
            'Table': table_name.capitalize(),
            'Source Records': f"{table_data['source_count']:,}",
            'Warehouse Records': f"{table_data['warehouse_count']:,}",
            'Missing Records': f"{table_data['missing_records']:,}",
            'Completeness': f"{table_data['completeness_percentage']:.1f}%",
            'Status': table_data['status'],
            'Business Impact': table_data['business_impact'][:50] + '...' if len(table_data['business_impact']) > 50 else table_data['business_impact']
        })
    
    df_detailed = pd.DataFrame(detailed_data)
    st.dataframe(df_detailed, use_container_width=True)
    
    # Business impact section
    st.subheader("💼 Business Impact Analysis")
    
    for table_name, table_data in data['tables'].items():
        with st.expander(f"{table_name.capitalize()} Impact"):
            st.info(f"**Status:** {table_data['status']}")
            st.warning(f"**Impact:** {table_data['business_impact']}")
            st.success(f"**Completeness:** {table_data['completeness_percentage']:.1f}%")
            
            if table_data['missing_records'] > 0:
                st.error(f"⚠️ {table_data['missing_records']} records are missing")
            else:
                st.success("✅ All records are present")
    
    # Validation timestamp
    st.caption(f"Last validated: {data['validation_timestamp']}")