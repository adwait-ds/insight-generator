from utils.insight_generation import generate_basic_insights
from utils.visualization import create_time_series_plot, create_campaign_bar_plot, create_channel_pie_chart, create_correlation_heatmap, create_top_performers_chart
from services.openai_service import OpenAIService
import numpy as np

class InsightAgent:
    def __init__(self):
        self.status = "Waiting for data validation"
        self.openai_service = OpenAIService()
    
    def generate_insights(self, df, validation_result, depth="Moderate", use_ai=True):
        """
        Generate insights from the validated data
        """
        self.status = "Starting analysis..."
        
        if use_ai:
            # Use OpenAI for insight generation
            insights = self.openai_service.generate_insights(df, validation_result, depth)
        else:
            # Use basic statistical insights
            insights = generate_basic_insights(df, validation_result, depth)
        
        self.status = "Insight generation complete"
        return insights
    
    def create_visualizations(self, df, validation_result):
        """
        Create visualizations based on available data with top N items
        """
        visualizations = {}
        
        # Time series plot
        if 'date' in validation_result["available_dimensions"]:
            time_metrics = [m for m in validation_result["available_metrics"] if m not in ['cpc', 'ctr', 'roi']]
            if time_metrics:
                visualizations['time_series'] = {
                    'metrics': time_metrics,
                    'default': time_metrics[0]
                }
        
        # Campaign performance (top 10 only)
        if 'campaign' in validation_result["available_dimensions"]:
            campaign_metrics = [m for m in validation_result["available_metrics"] if m not in ['cpc', 'ctr', 'roi']]
            if campaign_metrics:
                visualizations['campaign'] = {
                    'metrics': campaign_metrics,
                    'default': campaign_metrics[0],
                    'top_n': 10
                }
        
        # Channel performance (top 10 only)
        if all(d in validation_result["available_dimensions"] for d in ['source', 'medium']):
            channel_metrics = [m for m in validation_result["available_metrics"] if m not in ['cpc', 'ctr', 'roi']]
            if channel_metrics:
                visualizations['channel'] = {
                    'metrics': channel_metrics,
                    'default': channel_metrics[0],
                    'top_n': 10
                }
        
        # Device performance (if available)
        if 'device' in validation_result["available_dimensions"]:
            device_metrics = validation_result["available_metrics"]
            if device_metrics:
                visualizations['device'] = {
                    'metrics': device_metrics,
                    'default': device_metrics[0],
                    'top_n': 8
                }
        
        # Browser performance (if available)
        if 'browser' in validation_result["available_dimensions"]:
            browser_metrics = validation_result["available_metrics"]
            if browser_metrics:
                visualizations['browser'] = {
                    'metrics': browser_metrics,
                    'default': browser_metrics[0],
                    'top_n': 8
                }
        
        # Correlation heatmap
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 1:
            visualizations['correlation'] = True
        
        return visualizations