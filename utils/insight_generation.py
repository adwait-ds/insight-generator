import pandas as pd
import numpy as np

def generate_basic_insights(df, validation_result, depth="Moderate"):
    """
    Generate basic statistical insights (fallback when AI is not available)
    """
    insights = []
    
    available_metrics = validation_result["available_metrics"]
    available_dimensions = validation_result["available_dimensions"]
    
    # 1. Overall performance summary (if we have at least one metric)
    if available_metrics:
        first_metric = available_metrics[0]
        total_value = df[first_metric].sum()
        avg_value = df[first_metric].mean()
        insights.append(f"Total {first_metric}: {total_value:,.2f}")
        insights.append(f"Average {first_metric}: {avg_value:,.2f}")
    
    # 2. Basic metric calculations with available data
    if 'revenue' in df.columns and 'spend' in df.columns:
        total_revenue = df['revenue'].sum()
        total_spend = df['spend'].sum()
        if total_spend > 0:
            overall_roi = (total_revenue - total_spend) / total_spend
            insights.append(f"Overall ROI: {overall_roi:.2%}")
    
    if 'conversions' in df.columns and 'spend' in df.columns:
        total_conversions = df['conversions'].sum()
        if total_conversions > 0:
            cpa = df['spend'].sum() / total_conversions
            insights.append(f"Average CPA: ${cpa:.2f}")
    
    # 3. Time-based trends (if date is available)
    if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']):
        time_col = 'date'
        # Use the first available metric for time analysis
        if available_metrics:
            metric = available_metrics[0]
            time_grouped = df.groupby(pd.Grouper(key=time_col, freq='W'))[metric].sum().reset_index()
            if not time_grouped.empty:
                max_period = time_grouped.loc[time_grouped[metric].idxmax()]
                insights.append(f"Highest {metric} week: {max_period[time_col].strftime('%Y-%m-%d')} with {max_period[metric]:,.2f}")
    
    # 4. Dimension-based analysis (if we have at least one dimension)
    if available_dimensions:
        first_dimension = available_dimensions[0]
        if available_metrics:
            first_metric = available_metrics[0]
            dimension_grouped = df.groupby(first_dimension)[first_metric].sum().reset_index()
            dimension_grouped = dimension_grouped.sort_values(first_metric, ascending=False)
            
            if not dimension_grouped.empty:
                top_item = dimension_grouped.iloc[0]
                insights.append(f"Top {first_dimension} by {first_metric}: {top_item[first_dimension]} with {top_item[first_metric]:,.2f}")
    
    # 5. Simple correlations (if we have multiple metrics)
    if len(available_metrics) >= 2:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 1:
            # Simple correlation check between first two metrics
            if available_metrics[0] in numeric_cols and available_metrics[1] in numeric_cols:
                corr = df[available_metrics[0]].corr(df[available_metrics[1]])
                if not pd.isna(corr):
                    direction = "positively" if corr > 0 else "negatively"
                    insights.append(f"{available_metrics[0]} and {available_metrics[1]} are {direction} correlated (r={corr:.2f})")
    
    # If we have very few insights, add some general ones
    if len(insights) < 3:
        insights.append(f"Dataset contains {validation_result['rows']} rows with {validation_result['columns']} columns")
        insights.append(f"Found {len(available_metrics)} metrics and {len(available_dimensions)} dimensions for analysis")
    
    return insights