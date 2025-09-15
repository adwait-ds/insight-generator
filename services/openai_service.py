import openai
from config.config import Config
import pandas as pd
import json
import numpy as np
import re

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def generate_insights(self, df, validation_result, depth="Moderate"):
        """
        Generate insights using OpenAI API
        """
        # Prepare data summary for the prompt
        data_summary = self._prepare_data_summary(df, validation_result)
        
        prompt = self._build_insight_prompt(data_summary, depth)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marketing data analyst expert. Provide clear, actionable insights based on the data provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )
            
            insights = response.choices[0].message.content.strip()
            return self._parse_insights(insights)
            
        except Exception as e:
            return [f"Error generating insights: {str(e)}"]
    
    def _prepare_data_summary(self, df, validation_result):
        """Prepare a summary of the data for the prompt"""
        summary = {
            "data_shape": f"{validation_result['rows']} rows, {validation_result['columns']} columns",
            "available_metrics": validation_result["available_metrics"],
            "available_dimensions": validation_result["available_dimensions"],
            "missing_values": validation_result["missing_values"],
            "sample_data": df.head(10).to_dict('records'),
            "summary_stats": self._get_summary_statistics(df, validation_result["available_metrics"])
        }
        return summary
    
    def _get_summary_statistics(self, df, available_metrics):
        """Get summary statistics for numeric columns"""
        stats = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in available_metrics:
                stats[col] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "std": df[col].std()
                }
        return stats
    
    def _build_insight_prompt(self, data_summary, depth):
        """Build the prompt for OpenAI API without JSON serialization"""
        prompt = f"""
        Analyze this marketing data and provide {depth.lower()} insights:
        
        DATA OVERVIEW:
        - Shape: {data_summary['data_shape']}
        - Available metrics: {', '.join(data_summary['available_metrics'])}
        - Available dimensions: {', '.join(data_summary['available_dimensions'])}
        - Missing values: {data_summary['missing_values']}
        
        SUMMARY STATISTICS:
        """
        
        # Add summary statistics in a readable format
        for metric, stats in data_summary['summary_stats'].items():
            prompt += f"\n- {metric}: mean={stats['mean']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
        
        prompt += f"""
        
        SAMPLE DATA (first few rows):
        """
        
        # Add sample data in a readable format
        for i, row in enumerate(data_summary['sample_data'][:3]):  # First 3 rows only
            prompt += f"\nRow {i+1}: "
            for key, value in list(row.items())[:5]:  # First 5 columns only
                if isinstance(value, (int, float)):
                    prompt += f"{key}={value:.2f}, "
                else:
                    prompt += f"{key}='{value}', "
            prompt = prompt.rstrip(', ') + ";"
        
        prompt += """
        
        Please provide:
        1. Key performance insights with specific numbers and percentages
        2. Trends and patterns in the data
        3. Anomalies or outliers worth investigating
        4. Actionable recommendations for optimization
        5. Potential opportunities for growth
        
        Format the response as a clear, structured list of insights.
        Focus on marketing performance metrics like ROI, CPA, CTR, and conversion rates.
        """
        
        return prompt
    
    def _parse_insights(self, insights_text):
        """Parse the insights text into a list"""
        import re
        
        # If the response is already a list format, split it properly
        insights = []
        
        # Remove any markdown formatting
        insights_text = re.sub(r'\*\*|\*|`', '', insights_text)
        
        # Split by various list indicators
        lines = insights_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and section headers
            if not line or line.lower().startswith(('key insights', 'recommendations', 'conclusion')):
                continue
                
            # Check if this looks like an insight (not too short, not a header)
            if (len(line) > 20 and 
                not line.endswith(':') and 
                not line.isupper() and  # Skip all-caps headers
                not re.match(r'^[A-Z][a-z]+:', line)):  # Skip "Recommendation:" type lines
                
                # Clean up numbering and bullets
                line = re.sub(r'^[\d•\-*⁃]+[\s.]*', '', line).strip()
                
                if line and len(line) > 10:  # Minimum length for meaningful insight
                    insights.append(line)
        
        # If no insights were parsed, return the original text as a single insight
        if not insights:
            # Split into sentences for better formatting
            sentences = re.split(r'[.!?]+', insights_text)
            insights = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # If still no insights, return the first few meaningful lines
        if not insights:
            meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 30]
            insights = meaningful_lines[:5]  # Return first 5 meaningful lines
        
        return insights