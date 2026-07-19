"""
Data Quality Score dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from services.quality_service import QualityService
from utils.logger import get_logger
from utils.charts import create_gauge_chart

logger = get_logger()

def render_quality_score():
    """Render the data quality score dashboard."""
    st.title("⭐ Data Quality Score")
    st.caption("Comprehensive data quality scoring and monitoring")
    
    # Initialize service
    quality_service = QualityService()
    
    # Load data
    @st.cache_data(ttl=60)
    def load_quality_data():
        return quality_service.calculate_quality_score()
    
    data = load_quality_data()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Quality Score",
            f"{data['quality_score']:.1f}%",
            delta=f"Tier: {data['quality_tier']}"
        )
    
    with col2:
        component_count = len(data['components'])
        st.metric(
            "Components Evaluated",
            component_count,
            delta="✅ All components" if component_count > 0 else "❌ No data"
        )
    
    with col3:
        weights = data['components']
        best_component = max(weights.items(), key=lambda x: x[1]['score'])
        st.metric(
            "Best Component",
            best_component[0].replace('_', ' ').title(),
            delta=f"{best_component[1]['score']:.1f}%"
        )
    
    # Quality gauge
    st.subheader("📊 Quality Score Gauge")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig_gauge = create_gauge_chart(data['quality_score'], "Quality Score")
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Component breakdown
        components_data = []
        for name, comp in data['components'].items():
            components_data.append({
                'Component': name.replace('_', ' ').title(),
                'Score': comp['score'],
                'Weight': comp['weight'] * 100,
                'Weighted Score': comp['weighted_score']
            })
        
        df_components = pd.DataFrame(components_data)
        
        fig_components = px.bar(
            df_components,
            x='Component',
            y='Score',
            title='Component Scores',
            color='Score',
            color_continuous_scale='RdYlGn',
            range_y=[0, 100],
            text='Score'
        )
        fig_components.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_components.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig_components, use_container_width=True)
    
    # Detailed component analysis
    st.subheader("🔍 Component Analysis")
    
    for name, comp in data['components'].items():
        with st.expander(f"{name.replace('_', ' ').title()} Analysis"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score", f"{comp['score']:.1f}%")
            
            with col2:
                st.metric("Weight", f"{comp['weight']*100:.1f}%")
            
            with col3:
                st.metric("Weighted Score", f"{comp['weighted_score']:.1f}%")
            
            # Score gauge for this component
            fig_gauge_comp = create_gauge_chart(comp['score'], name.replace('_', ' ').title())
            st.plotly_chart(fig_gauge_comp, use_container_width=True)
    
    # Quality recommendations
    st.subheader("💡 Recommendations")
    
    quality_tier = data['quality_tier']
    if quality_tier == "EXCELLENT":
        st.success("✅ Your data quality is excellent! Continue maintaining current standards.")
        
        st.info("**Maintenance Recommendations:**")
        st.write("• Continue regular monitoring of all quality components")
        st.write("• Implement automated alerts for any quality degradation")
        st.write("• Review and update quality thresholds periodically")
        
    elif quality_tier == "GOOD":
        st.warning("⚠️ Good quality with minor improvements needed.")
        
        poor_components = [name for name, comp in data['components'].items() 
                          if comp['score'] < 90]
        
        if poor_components:
            st.warning(f"**Focus Areas:** {', '.join([c.replace('_', ' ').title() for c in poor_components])}")
            st.write("• Review and improve these components to reach EXCELLENT tier")
            st.write("• Implement targeted data quality improvements")
            st.write("• Increase monitoring frequency for these components")
    
    else:
        st.error("🔴 Poor quality detected. Immediate action required.")
        
        critical_components = [name for name, comp in data['components'].items() 
                              if comp['score'] < 80]
        
        if critical_components:
            st.error(f"**Critical Issues:** {', '.join([c.replace('_', ' ').title() for c in critical_components])}")
            st.write("• **URGENT:** Address critical quality issues immediately")
            st.write("• Perform root cause analysis for poor quality components")
            st.write("• Implement data quality improvement initiatives")
            st.write("• Establish data quality governance framework")
    
    # Validation timestamp
    st.caption(f"Last validated: {data['validation_timestamp']}")