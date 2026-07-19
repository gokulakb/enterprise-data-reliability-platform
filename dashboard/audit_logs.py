"""
Audit Logs dashboard page.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from database.database import get_db_session
from database.models import AuditLog
from utils.logger import get_logger

logger = get_logger()

def render_audit_logs():
    """Render the audit logs dashboard."""
    st.title("📋 Audit Logs")
    st.caption("Comprehensive audit trail for all platform activities")
    
    # Initialize session
    session = get_db_session()
    
    # Filters
    st.subheader("🔍 Filter Audit Logs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
    
    with col2:
        actions = ['all', 'dashboard_view', 'report_export', 'data_validation', 
                  'signoff_approval', 'alert_acknowledge', 'threshold_update',
                  'pipeline_trigger', 'data_refresh']
        selected_action = st.selectbox("Action Type", actions)
    
    with col3:
        statuses = ['all', 'PASS', 'WARNING', 'FAIL', 'PENDING']
        selected_status = st.selectbox("Status", statuses)
    
    # Load audit logs
    @st.cache_data(ttl=60)
    def load_audit_logs(start_date, end_date, action, status):
        try:
            query = session.query(AuditLog)
            
            if start_date and end_date:
                query = query.filter(AuditLog.timestamp >= start_date)
                query = query.filter(AuditLog.timestamp <= end_date + timedelta(days=1))
            
            if action != 'all':
                query = query.filter(AuditLog.action == action)
            
            if status != 'all':
                query = query.filter(AuditLog.status == status)
            
            query = query.order_by(AuditLog.timestamp.desc()).limit(500)
            results = query.all()
            
            return [log.to_dict() for log in results]
        except Exception as e:
            logger.error(f"Error loading audit logs: {str(e)}")
            return []
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        logs = load_audit_logs(start_date, end_date, selected_action, selected_status)
    else:
        logs = []
    
    if not logs:
        st.warning("No audit logs found.")
        return
    
    df = pd.DataFrame(logs)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Logs", len(df))
    
    with col2:
        unique_actions = df['action'].nunique()
        st.metric("Unique Actions", unique_actions)
    
    with col3:
        unique_users = df['user'].nunique()
        st.metric("Active Users", unique_users)
    
    with col4:
        pass_count = (df['status'] == 'PASS').sum()
        pass_rate = (pass_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    
    # Charts
    st.subheader("📊 Audit Log Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Action distribution
        action_counts = df['action'].value_counts().head(10)
        fig_actions = px.pie(
            values=action_counts.values,
            names=action_counts.index,
            title='Action Distribution'
        )
        fig_actions.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig_actions, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = df['status'].value_counts()
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title='Status Distribution',
            color=status_counts.index,
            color_discrete_map={
                'PASS': 'green',
                'WARNING': 'orange',
                'FAIL': 'red',
                'PENDING': 'blue'
            }
        )
        fig_status.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Time series analysis
    st.subheader("📈 Activity Over Time")
    
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        
        fig_timeline = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Daily Activity Logs'
        )
        fig_timeline.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Detailed logs table
    st.subheader("📋 Log Details")
    
    # Prepare display dataframe
    display_df = df[['timestamp', 'user', 'action', 'metric_type', 'metric_value', 'status', 'details']].copy()
    
    # Format for display
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Add status badges
    def status_badge(status):
        colors = {
            'PASS': '🟢',
            'WARNING': '🟡',
            'FAIL': '🔴',
            'PENDING': '🔵'
        }
        return f"{colors.get(status, '⚪')} {status}"
    
    display_df['status_display'] = display_df['status'].apply(status_badge)
    
    # Select columns for display
    display_cols = ['timestamp', 'user', 'action', 'metric_type', 'metric_value', 'status_display', 'details']
    display_df = display_df[display_cols]
    display_df.columns = ['Timestamp', 'User', 'Action', 'Metric Type', 'Value', 'Status', 'Details']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Export button
    if st.button("📤 Export Audit Logs (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )