"""
Chart creation utilities for Plotly and Matplotlib.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional

def create_gauge_chart(value: float, title: str = "Metric Score", 
                       min_val: float = 0, max_val: float = 100) -> go.Figure:
    """Create a gauge chart for a metric value."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 95},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkgreen" if value >= 95 else "orange" if value >= 80 else "red"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, max_val * 0.7], 'color': 'rgba(255, 0, 0, 0.3)'},
                {'range': [max_val * 0.7, max_val * 0.85], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [max_val * 0.85, max_val * 0.95], 'color': 'rgba(255, 255, 0, 0.3)'},
                {'range': [max_val * 0.95, max_val], 'color': 'rgba(0, 255, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.95
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_metric_card(value: float, title: str, max_value: float = 100) -> go.Figure:
    """Create a metric card with progress bar."""
    fig = go.Figure(go.Indicator(
        mode="number+delta+gauge",
        value=value,
        title={'text': title},
        delta={'reference': max_value * 0.95},
        gauge={
            'shape': "bullet",
            'axis': {'range': [0, max_value]},
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': max_value * 0.95
            },
            'steps': [
                {'range': [0, max_value * 0.7], 'color': "lightgray"},
                {'range': [max_value * 0.7, max_value * 0.9], 'color': "gray"},
                {'range': [max_value * 0.9, max_value], 'color': "darkgray"}
            ]
        }
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return fig

def create_timeline_chart(data: pd.DataFrame, date_col: str, value_col: str, 
                         title: str = "Timeline") -> go.Figure:
    """Create a timeline chart with area fill."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data[date_col],
        y=data[value_col],
        mode='lines+markers',
        name='Value',
        fill='tozeroy',
        line=dict(color='royalblue', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_kpi_card(value: Any, title: str, subtitle: str = "", 
                   delta: Optional[float] = None) -> go.Figure:
    """Create a KPI card visualization."""
    fig = go.Figure(go.Indicator(
        mode="number",
        value=value,
        title={'text': title},
        number={'font': {'size': 40}}
    ))
    
    if delta is not None:
        fig.add_trace(go.Indicator(
            mode="delta",
            value=value,
            delta={'reference': value - delta, 'relative': True}
        ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                     title: str = "", color_col: Optional[str] = None) -> go.Figure:
    """Create a bar chart."""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=color_col if color_col else None,
        text_auto=True
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                      title: str = "", color_col: Optional[str] = None) -> go.Figure:
    """Create a line chart."""
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=color_col if color_col else None
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, 
                     title: str = "") -> go.Figure:
    """Create a pie chart."""
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title,
        hole=0.3
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_heatmap(df: pd.DataFrame, title: str = "") -> go.Figure:
    """Create a heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale='RdYlGn',
        text=df.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig