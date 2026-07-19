"""
Main Streamlit application entry point.
Enterprise Data Reliability Platform
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import APP_NAME, APP_VERSION
from utils.logger import get_logger
from database.create_tables import init_database
from database.seed_data import seed_database

# Configure page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger()

# Initialize database
try:
    if init_database():
        logger.info("Database initialized successfully")
        # Seed data if needed
        seed_database()
    else:
        logger.warning("Database initialization issue - data may be missing")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
    }
    .status-pass {
        background-color: #28a745;
        color: white;
    }
    .status-warning {
        background-color: #ffc107;
        color: black;
    }
    .status-fail {
        background-color: #dc3545;
        color: white;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📊 Data Reliability")
    st.markdown("---")
    
    # Navigation
    st.subheader("Navigation")
    page = st.radio(
        "Select Dashboard",
        [
            "🏢 Executive Overview",
            "📊 Data Completeness",
            "⏰ Data Freshness",
            "🔄 Source vs Warehouse",
            "🔄 Pipeline Health",
            "⭐ Data Quality Score",
            "✅ Reliability Sign-off",
            "⚠️ Alerts",
            "📋 Audit Logs",
            "📤 Export Center"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # Application info
    st.caption(f"Version: {APP_VERSION}")
    st.caption("© 2024 Enterprise Data Platform")
    
    # Auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    if auto_refresh:
        st.caption("🔄 Auto-refresh enabled")

# Main content
try:
    if page == "🏢 Executive Overview":
        from dashboard.overview import render_overview
        render_overview()
    
    elif page == "📊 Data Completeness":
        from dashboard.completeness import render_completeness
        render_completeness()
    
    elif page == "⏰ Data Freshness":
        from dashboard.freshness import render_freshness
        render_freshness()
    
    elif page == "🔄 Source vs Warehouse":
        from dashboard.reconciliation import render_reconciliation
        render_reconciliation()
    
    elif page == "🔄 Pipeline Health":
        from dashboard.pipeline_health import render_pipeline_health
        render_pipeline_health()
    
    elif page == "⭐ Data Quality Score":
        from dashboard.quality_score import render_quality_score
        render_quality_score()
    
    elif page == "✅ Reliability Sign-off":
        from dashboard.signoff import render_signoff
        render_signoff()
    
    elif page == "⚠️ Alerts":
        from dashboard.alerts import render_alerts
        render_alerts()
    
    elif page == "📋 Audit Logs":
        from dashboard.audit_logs import render_audit_logs
        render_audit_logs()
    
    elif page == "📤 Export Center":
        from dashboard.export_center import render_export_center
        render_export_center()
    
    # Auto-refresh logic
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

except Exception as e:
    logger.error(f"Error rendering dashboard: {str(e)}")
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check the application logs for more details.")