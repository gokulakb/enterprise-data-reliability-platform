"""
Reliability Sign-off dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from services.signoff_service import SignOffService
from utils.logger import get_logger

logger = get_logger()

def render_signoff():
    """Render the reliability sign-off dashboard."""
    st.title("✅ Reliability Sign-off")
    st.caption("Automated data reliability sign-off and approval")
    
    # Initialize service
    signoff_service = SignOffService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_signoff():
        return signoff_service.generate_sign_off()
    
    data = load_signoff()
    
    # Sign-off header
    status = data['sign_off_status']
    
    status_icons = {
        'PASS': '✅',
        'WARNING': '⚠️',
        'FAIL': '❌'
    }
    
    status_colors = {
        'PASS': 'green',
        'WARNING': 'orange',
        'FAIL': 'red'
    }
    
    st.markdown(f"""
    <div style="
        background-color: {status_colors[status]}20;
        padding: 2rem;
        border-radius: 1rem;
        border-left: 5px solid {status_colors[status]};
        margin-bottom: 2rem;
    ">
        <h1 style="margin: 0; color: {status_colors[status]};">
            {status_icons[status]} Sign-off Status: {status}
        </h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    st.subheader("📊 Sign-off Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Quality Score",
            f"{data['quality_score']:.1f}%",
            delta=f"Tier: {data['quality_tier']}"
        )
    
    with col2:
        st.metric(
            "Freshness Score",
            f"{data['freshness_score']:.1f}%",
            delta="✅" if data['freshness_score'] >= 95 else "⚠️"
        )
    
    with col3:
        st.metric(
            "Completeness Score",
            f"{data['completeness_score']:.1f}%",
            delta="✅" if data['completeness_score'] >= 99 else "⚠️"
        )
    
    with col4:
        st.metric(
            "Reconciliation Score",
            f"{data['reconciliation_score']:.1f}%",
            delta="✅" if data['reconciliation_score'] >= 98 else "⚠️"
        )
    
    # Detailed checks
    st.subheader("📋 Sign-off Checklist")
    
    checks = {
        'Completeness Check': data['completeness_score'] >= 99,
        'Freshness Check': data['freshness_score'] >= 95,
        'Reconciliation Check': data['reconciliation_score'] >= 98,
        'Quality Threshold': data['quality_score'] >= 98,
        'Pipeline Health': data['pipeline_health'] == 'HEALTHY' or data['pipeline_health'] == 'WARNING'
    }
    
    for check, passed in checks.items():
        status_icon = '✅' if passed else '❌'
        color = 'green' if passed else 'red'
        
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background-color: {color}10;
            border-radius: 0.5rem;
            border-left: 3px solid {color};
        ">
            <span style="font-weight: bold;">{check}</span>
            <span style="font-size: 1.5rem;">{status_icon}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    for rec in data['recommendations']:
        if 'URGENT' in rec:
            st.error(f"🚨 {rec}")
        elif 'review' in rec.lower() or 'investigate' in rec.lower():
            st.warning(f"⚠️ {rec}")
        else:
            st.success(f"✅ {rec}")
    
    # Validation timestamp
    st.caption(f"Last validated: {data['sign_off_timestamp']}")