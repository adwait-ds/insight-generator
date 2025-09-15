import pandas as pd
import numpy as np
import re
from datetime import datetime

def validate_data_structure(df):
    """
    Validate the structure of marketing data using contains syntax
    """
    # Normalize column names (lowercase and remove special characters)
    df.columns = [re.sub(r'[^a-zA-Z0-9]', '', col.lower()) for col in df.columns]
    
    # Define patterns for required metrics and dimensions
    metric_patterns = {
        'spend': r'spend|cost|investment|budget',
        'cost': r'cost|expense|expenditure',
        'cpc': r'cpc|costperclick|cost_per_click',
        'ctr': r'ctr|clickthroughrate|click_through_rate',
        'roi': r'roi|returnoninvestment|return_on_investment',
        'transactions': r'transaction|purchase|sale',
        'conversions': r'conversion|convert',
        'revenue': r'revenue|income|sales'
    }
    
    dimension_patterns = {
        'date': r'date|time|day|week|month|year',
        'campaign': r'campaign|promo|promotion|initiative',
        'source': r'source|origin|trafficsource|traffic_source',
        'medium': r'medium|channel|type',
        'city': r'city|town|metro',
        'state': r'state|province|region',
        'age': r'age|yearold|years',
        'gender': r'gender|sex',
        'device': r'device|platform|hardware',
        'browser': r'browser|useragent|user_agent'
    }
    
    # Find matching columns for each pattern
    available_metrics = []
    for metric_name, pattern in metric_patterns.items():
        matching_cols = [col for col in df.columns if re.search(pattern, col, re.IGNORECASE)]
        if matching_cols:
            available_metrics.append(metric_name)
            # Rename the first matching column to standard name for easier processing
            if metric_name not in df.columns and matching_cols:
                df = df.rename(columns={matching_cols[0]: metric_name})
    
    available_dimensions = []
    for dimension_name, pattern in dimension_patterns.items():
        matching_cols = [col for col in df.columns if re.search(pattern, col, re.IGNORECASE)]
        if matching_cols:
            available_dimensions.append(dimension_name)
            # Rename the first matching column to standard name for easier processing
            if dimension_name not in df.columns and matching_cols:
                df = df.rename(columns={matching_cols[0]: dimension_name})
    
    # Check data types and convert date if needed
    if 'date' in df.columns:
        df = convert_date_column(df, 'date')
    
    # Check for missing values
    missing_values = df.isnull().sum().sum()
    
    # UPDATED: Only require 1 metric and 1 dimension (was 3 metrics and 2 dimensions)
    validation_result = {
        "has_sufficient_data": len(available_metrics) >= 1 and len(available_dimensions) >= 1,
        "available_metrics": available_metrics,
        "available_dimensions": available_dimensions,
        "missing_values": missing_values,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "original_columns": list(df.columns)
    }
    
    return validation_result, df

def convert_date_column(df, date_col):
    """
    Convert date column to datetime format with multiple fallback strategies
    """
    if date_col in df.columns:
        # Try multiple date parsing strategies
        try:
            # First try direct conversion
            df[date_col] = pd.to_datetime(df[date_col])
        except:
            try:
                # Try with different date formats
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            except:
                try:
                    # Try inferring datetime format
                    df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True)
                except:
                    # If all fails, try to extract dates from strings
                    df[date_col] = df[date_col].apply(extract_date_from_string)
        
        # Drop rows where date conversion failed
        original_count = len(df)
        df = df.dropna(subset=[date_col])
        dropped_count = original_count - len(df)
        
        if dropped_count > 0:
            print(f"Warning: Dropped {dropped_count} rows with invalid dates")
    
    return df

def extract_date_from_string(date_str):
    """
    Extract date from various string formats
    """
    if pd.isna(date_str) or date_str == '':
        return pd.NaT
    
    # Common date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',   # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}',   # MM-DD-YYYY
        r'\d{4}/\d{2}/\d{2}',   # YYYY/MM/DD
        r'\d{1,2} [A-Za-z]{3} \d{4}',  # 01 Jan 2023
        r'[A-Za-z]{3} \d{1,2}, \d{4}',  # Jan 01, 2023
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, str(date_str))
        if match:
            try:
                return pd.to_datetime(match.group())
            except:
                continue
    
    return pd.NaT

def generate_sample_data():
    """
    Generate sample marketing data for testing with proper datetime format
    """
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    campaigns = ['Spring_Sale', 'Summer_Promo', 'Fall_Campaign', 'Winter_Offer']
    sources = ['Google', 'Facebook', 'Instagram', 'Twitter', 'Email']
    mediums = ['CPC', 'Social', 'Organic', 'Display']
    
    data = {
        'date': np.random.choice(dates, 500),
        'campaign': np.random.choice(campaigns, 500),
        'source': np.random.choice(sources, 500),
        'medium': np.random.choice(mediums, 500),
        'spend': np.random.uniform(50, 2000, 500),
        'impressions': np.random.randint(1000, 50000, 500),
        'clicks': np.random.randint(10, 500, 500),
        'conversions': np.random.randint(0, 50, 500),
        'revenue': np.random.uniform(0, 5000, 500),
    }
    
    data['cpc'] = data['spend'] / data['clicks']
    data['ctr'] = data['clicks'] / data['impressions']
    data['roi'] = (data['revenue'] - data['spend']) / data['spend']
    
    df = pd.DataFrame(data)
    
    # Ensure date column is proper datetime
    df['date'] = pd.to_datetime(df['date'])
    
    return df