import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_time_series_plot(df, time_col, metric):
    """
    Create a time series plot for the given metric with proper date handling
    """
    # Ensure the date column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        # Drop rows with invalid dates
        df = df.dropna(subset=[time_col])
    
    # Group by week for better visualization
    try:
        time_grouped = df.groupby(pd.Grouper(key=time_col, freq='W'))[metric].sum().reset_index()
        time_grouped = time_grouped.sort_values(time_col)
        
        fig = px.line(time_grouped, x=time_col, y=metric, 
                     title=f"{metric.title()} Over Time (Weekly Aggregation)",
                     labels={time_col: 'Date', metric: metric.title()})
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=metric.title(),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        # Fallback: use daily aggregation if weekly fails
        time_grouped = df.groupby(time_col)[metric].sum().reset_index()
        time_grouped = time_grouped.sort_values(time_col)
        
        fig = px.line(time_grouped, x=time_col, y=metric, 
                     title=f"{metric.title()} Over Time (Daily)",
                     labels={time_col: 'Date', metric: metric.title()})
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=metric.title(),
            hovermode='x unified'
        )
        
        return fig

def create_campaign_bar_plot(df, campaign_col, metric):
    """
    Create a bar plot for campaign performance (top 10 only)
    """
    # Get top 10 campaigns by the selected metric
    campaign_grouped = df.groupby(campaign_col)[metric].sum().reset_index()
    campaign_grouped = campaign_grouped.sort_values(metric, ascending=False).head(10)
    
    # Use color scale based on metric value
    fig = px.bar(campaign_grouped, x=campaign_col, y=metric,
                title=f"Top 10 Campaigns by {metric.title()}",
                labels={campaign_col: 'Campaign', metric: metric.title()},
                color=metric,
                color_continuous_scale='Blues')
    
    fig.update_layout(
        xaxis_title="Campaign",
        yaxis_title=metric.title(),
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def create_channel_pie_chart(df, metric):
    """
    Create a pie chart for channel performance (top 10 channels)
    """
    # Group by source and medium, get top 10
    channel_grouped = df.groupby(['source', 'medium'])[metric].sum().reset_index()
    channel_grouped = channel_grouped.sort_values(metric, ascending=False).head(10)
    channel_grouped['channel'] = channel_grouped['source'] + ' - ' + channel_grouped['medium']
    
    # Create donut chart for better visualization
    fig = px.pie(channel_grouped, values=metric, names='channel',
                title=f"Top 10 Channels by {metric.title()}",
                hole=0.4)  # Donut chart
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    
    return fig

def create_correlation_heatmap(df):
    """
    Create a correlation heatmap for numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) > 1:
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        fig = px.imshow(corr_matrix, 
                       title="Correlation Matrix of Metrics",
                       color_continuous_scale='RdBu_r',
                       zmin=-1, zmax=1,
                       aspect="auto")
        
        # Add correlation values as annotations
        fig.update_layout(
            xaxis_title="Metrics",
            yaxis_title="Metrics"
        )
        
        return fig
    return None

def create_top_performers_chart(df, dimension_col, metric_col, chart_type='bar', top_n=10):
    """
    Generic function to create charts for top performers
    """
    # Group and get top N
    grouped = df.groupby(dimension_col)[metric_col].sum().reset_index()
    grouped = grouped.sort_values(metric_col, ascending=False).head(top_n)
    
    if chart_type == 'bar':
        fig = px.bar(grouped, x=dimension_col, y=metric_col,
                    title=f"Top {top_n} {dimension_col.title()} by {metric_col.title()}",
                    labels={dimension_col: dimension_col.title(), metric_col: metric_col.title()},
                    color=metric_col,
                    color_continuous_scale='Viridis')
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False
        )
        
    elif chart_type == 'pie':
        fig = px.pie(grouped, values=metric_col, names=dimension_col,
                    title=f"Top {top_n} {dimension_col.title()} by {metric_col.title()}",
                    hole=0.3)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig