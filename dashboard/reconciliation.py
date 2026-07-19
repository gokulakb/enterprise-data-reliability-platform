"""
Source to Warehouse Reconciliation dashboard page.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from services.reconciliation_service import ReconciliationService
from utils.logger import get_logger

logger = get_logger()

def render_reconciliation():
    """Render the source to warehouse reconciliation dashboard."""
    st.title("🔄 Source vs Warehouse Reconciliation")
    st.caption("Compare source and warehouse data to identify discrepancies")
    
    # Initialize service
    reconciliation_service = ReconciliationService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_reconciliation():
        return reconciliation_service.reconcile_all_tables()
    
    data = load_reconciliation()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Match %",
            f"{data['overall_match']:.1f}%",
            delta="✅" if data['overall_match'] >= 98 else "⚠️"
        )
    
    with col2:
        total_missing = sum(t.get('missing_in_warehouse', 0) for t in data['tables'].values())
        st.metric(
            "Missing Records",
            total_missing,
            delta=f"{'⚠️' if total_missing > 0 else '✅'}"
        )
    
    with col3:
        total_extra = sum(t.get('extra_in_warehouse', 0) for t in data['tables'].values())
        st.metric(
            "Extra Records",
            total_extra,
            delta=f"{'⚠️' if total_extra > 0 else '✅'}"
        )
    
    with col4:
        total_duplicates = sum(
            t.get('source_duplicates', 0) + t.get('warehouse_duplicates', 0) 
            for t in data['tables'].values()
        )
        st.metric(
            "Total Duplicates",
            total_duplicates,
            delta=f"{'⚠️' if total_duplicates > 0 else '✅'}"
        )
    
    # Reconciliation by table
    st.subheader("📋 Reconciliation by Table")
    
    tables_data = []
    for table_name, table_data in data['tables'].items():
        tables_data.append({
            'Table': table_name.capitalize(),
            'Match %': table_data['match_percentage'],
            'Source Count': table_data['source_count'],
            'Warehouse Count': table_data['warehouse_count'],
            'Missing': table_data.get('missing_in_warehouse', 0),
            'Extra': table_data.get('extra_in_warehouse', 0),
            'Duplicates': table_data.get('source_duplicates', 0) + table_data.get('warehouse_duplicates', 0),
            'Mismatches': table_data.get('mismatches', 0),
            'Status': table_data['status']
        })
    
    df_tables = pd.DataFrame(tables_data)
    
    # Match percentage chart
    fig = px.bar(
        df_tables,
        x='Table',
        y='Match %',
        title='Reconciliation Match Percentage by Table',
        color='Match %',
        color_continuous_scale='RdYlGn',
        range_y=[0, 100],
        text='Match %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Discrepancy analysis
    st.subheader("🔍 Discrepancy Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Discrepancy types by table
        fig_discrepancies = go.Figure()
        
        for table in df_tables['Table']:
            table_data = data['tables'][table.lower()]
            fig_discrepancies.add_trace(go.Bar(
                name=table,
                x=['Missing', 'Extra', 'Duplicates', 'Mismatches'],
                y=[
                    table_data.get('missing_in_warehouse', 0),
                    table_data.get('extra_in_warehouse', 0),
                    table_data.get('source_duplicates', 0) + table_data.get('warehouse_duplicates', 0),
                    table_data.get('mismatches', 0)
                ],
                textposition='auto'
            ))
        
        fig_discrepancies.update_layout(
            title='Discrepancy Types by Table',
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig_discrepancies, use_container_width=True)
    
    with col2:
        # Table details
        st.info("**Table Reconciliation Status**")
        
        for table_name, table_data in data['tables'].items():
            status_color = {
                'PASS': '🟢',
                'WARNING': '🟡',
                'FAIL': '🔴'
            }.get(table_data['status'], '⚪')
            
            st.write(f"{status_color} **{table_name.capitalize()}**: {table_data['status']}")
            st.write(f"  Match: {table_data['match_percentage']:.1f}%")
            st.write(f"  Missing: {table_data.get('missing_in_warehouse', 0)}")
            st.write(f"  Extra: {table_data.get('extra_in_warehouse', 0)}")
            st.write("---")
    
    # Validation timestamp
    st.caption(f"Last validated: {data['validation_timestamp']}")