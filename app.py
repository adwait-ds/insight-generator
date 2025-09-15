import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re

# Import agents
from agents.validation_agent import ValidationAgent
from agents.insight_agent import InsightAgent

# Import utils
from utils.data_validation import generate_sample_data
from utils.visualization import create_time_series_plot, create_campaign_bar_plot, create_channel_pie_chart, create_correlation_heatmap, create_top_performers_chart

# Set page configuration
st.set_page_config(
    page_title="Marketing Insight Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 5px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">Marketing Insight Generator</h1>', unsafe_allow_html=True)
st.markdown("""
This multi-agent system analyzes your marketing data to generate actionable insights. 
Upload your CSV or Excel file containing marketing metrics and dimensions.
""")

# Initialize session state
if 'data_processed' not in st.session_state:
    st.session_state.data_processed = False
if 'insights_generated' not in st.session_state:
    st.session_state.insights_generated = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None

# Initialize agents
if 'validation_agent' not in st.session_state:
    st.session_state.validation_agent = ValidationAgent()
if 'insight_agent' not in st.session_state:
    st.session_state.insight_agent = InsightAgent()

# Sidebar for file upload and controls
with st.sidebar:
    st.header("Data Upload")
    uploaded_file = st.file_uploader(
        "Upload your marketing data (CSV or Excel)",
        type=['csv', 'xlsx'],
        help="File should contain marketing metrics like spends, costs, CPC, CTR, ROI, etc."
    )
    
    st.header("Configuration")
    sample_data = st.checkbox("Use sample data", value=False)
    insight_depth = st.select_slider(
        "Insight Depth",
        options=["Basic", "Moderate", "Detailed"],
        value="Moderate"
    )
    
    # OpenAI configuration
    st.header("AI Settings")
    use_ai = st.checkbox("Use AI for insights", value=True)
    
    if use_ai:
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Required for AI-powered insights")
        
        # Model selection
        model_options = {
            "GPT-4 Turbo (Recommended)": "gpt-4-1106-preview",
            "GPT-4": "gpt-4",
            "GPT-3.5 Turbo (Fast)": "gpt-3.5-turbo-1106",
            "GPT-3.5 Turbo (Fastest)": "gpt-3.5-turbo"
        }
        
        selected_model = st.selectbox(
            "AI Model",
            options=list(model_options.keys()),
            index=0
        )
        
        model_name = model_options[selected_model]
        
        # Show model info
        with st.expander("Model Information"):
            if model_name == "gpt-4-1106-preview":
                st.info("**GPT-4 Turbo**: Most capable model, 128K context, best for complex analysis")
            elif model_name == "gpt-4":
                st.info("**GPT-4**: High quality, reliable, 8K context")
            elif model_name == "gpt-3.5-turbo-1106":
                st.info("**GPT-3.5 Turbo**: Fast and cost-effective, 16K context")
            else:
                st.info("**GPT-3.5 Turbo**: Fastest option, good for basic analysis, 4K context")
    
    if st.button("Generate Insights", disabled=not uploaded_file and not sample_data):
        st.session_state.insights_generated = False
        st.session_state.data_processed = False
        st.session_state.validation_result = None
        st.session_state.processed_df = None

# Main app logic
if sample_data or uploaded_file is not None:
    # Load data
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.stop()
    else:
        df = generate_sample_data()
    
    st.session_state.df = df
    
    # Display raw data
    with st.expander("View Raw Data"):
        st.dataframe(df.head(20))
        st.write(f"Data shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Agent 1: Data Validation
    st.markdown('<h2 class="sub-header">Data Validation</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        validation_progress = st.progress(0)
        status_text = st.empty()
    
    for i in range(101):
        validation_progress.progress(i)
        status_text.text(f"Agent 1: {st.session_state.validation_agent.status}")
        if i == 100:
            break
    
    try:
        validation_result, processed_df = st.session_state.validation_agent.process_data(df)
        st.session_state.validation_result = validation_result
        st.session_state.processed_df = processed_df
        
        # Double-check date conversion
        date_conversion_issue = False
        if 'date' in processed_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(processed_df['date']):
                date_conversion_issue = True
                st.markdown('<div class="warning-box">⚠️ Date column could not be automatically converted. Time series visualizations will be limited.</div>', unsafe_allow_html=True)
        
        if validation_result["has_sufficient_data"]:
            st.success("✅ Data validation passed! Sufficient data for analysis.")
            
            # Show validation details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Available Metrics", len(validation_result["available_metrics"]))
                st.caption(", ".join(validation_result["available_metrics"][:3]) + ("..." if len(validation_result["available_metrics"]) > 3 else ""))
            with col2:
                st.metric("Available Dimensions", len(validation_result["available_dimensions"]))
                st.caption(", ".join(validation_result["available_dimensions"][:3]) + ("..." if len(validation_result["available_dimensions"]) > 3 else ""))
            with col3:
                st.metric("Missing Values", validation_result["missing_values"])
                st.caption(f"Total rows: {validation_result['rows']}")
            
            # # Show column mappings if available
            # with st.expander("View Column Mappings"):
            #     from utils.data_validation import detect_column_mappings
            #     column_mappings = detect_column_mappings(df)
                
            #     st.write("Detected column mappings:")
            #     for col, mapping in column_mappings.items():
            #         if mapping['type'] != 'unknown':
            #             st.write(f"• **{col}** → {mapping['type']}: {mapping['standard_name']}")
            #         else:
            #             st.write(f"• **{col}** → unknown (will not be used in analysis)")
            
            # Agent 2: Insight Generation
            st.markdown('<h2 class="sub-header">Insight Generation</h2>', unsafe_allow_html=True)
            
            insight_progress = st.progress(0)
            insight_status = st.empty()
            
            for i in range(101):
                insight_progress.progress(i)
                insight_status.text(f"Agent 2: {st.session_state.insight_agent.status}")
                if i == 100:
                    break
            
            # Set OpenAI API key if provided
            if use_ai and openai_api_key:
                import os
                os.environ['OPENAI_API_KEY'] = openai_api_key
            
            insights = st.session_state.insight_agent.generate_insights(
                processed_df, validation_result, insight_depth, use_ai
            )
            
            # Display insights
            st.markdown("### Key Insights")
            
            if insights and isinstance(insights, list) and len(insights) > 0:
                for i, insight in enumerate(insights, 1):
                    insight = str(insight).strip()
                    if insight and insight != "None" and len(insight) > 10:
                        st.markdown(f"""
                        <div class="insight-box">
                            <strong>Insight #{i}:</strong> {insight}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("""
                No insights were generated. This could be because:
                - The AI model didn't return structured insights
                - There was an error in processing the data
                - The data might be too limited for meaningful analysis
                """)
                
                # Show fallback basic insights
                st.info("Generating basic statistical insights instead...")
                from utils.insight_generation import generate_basic_insights
                basic_insights = generate_basic_insights(processed_df, validation_result, insight_depth)
                
                for i, insight in enumerate(basic_insights, 1):
                    if insight and len(insight) > 10:
                        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
            
            # Visualizations
            st.markdown("### Visualizations")
            
            # Get available visualizations
            available_viz = st.session_state.insight_agent.create_visualizations(processed_df, validation_result)
            
            # Handle date conversion issues
            if date_conversion_issue and 'time_series' in available_viz:
                del available_viz['time_series']
                st.info("Time series visualizations disabled due to date format issues.")
            
            # Create tabs for different visualizations
            tab_names = []
            if 'time_series' in available_viz:
                tab_names.append("Performance Over Time")
            if 'campaign' in available_viz:
                tab_names.append("Campaign Analysis")
            if 'channel' in available_viz:
                tab_names.append("Channel Performance")
            if 'device' in available_viz:
                tab_names.append("Device Performance")
            if 'browser' in available_viz:
                tab_names.append("Browser Performance")
            if 'correlation' in available_viz:
                tab_names.append("Correlation Analysis")
            
            if tab_names:
                tabs = st.tabs(tab_names)
                tab_idx = 0
                
                # Time series plot
                if 'time_series' in available_viz:
                    with tabs[tab_idx]:
                        time_metric = st.selectbox(
                            "Select metric for time series", 
                            options=available_viz['time_series']['metrics'],
                            key="time_metric"
                        )
                        fig = create_time_series_plot(processed_df, 'date', time_metric)
                        st.plotly_chart(fig, use_container_width=True)
                    tab_idx += 1
                
                # Campaign performance
                if 'campaign' in available_viz:
                    with tabs[tab_idx]:
                        campaign_metric = st.selectbox(
                            "Select metric for campaign comparison", 
                            options=available_viz['campaign']['metrics'],
                            key="campaign_metric"
                        )
                        fig = create_campaign_bar_plot(processed_df, 'campaign', campaign_metric)
                        st.plotly_chart(fig, use_container_width=True)
                    tab_idx += 1
                
                # Channel performance
                if 'channel' in available_viz:
                    with tabs[tab_idx]:
                        channel_metric = st.selectbox(
                            "Select metric for channel analysis", 
                            options=available_viz['channel']['metrics'],
                            key="channel_metric"
                        )
                        fig = create_channel_pie_chart(processed_df, channel_metric)
                        st.plotly_chart(fig, use_container_width=True)
                    tab_idx += 1
                
                # Device performance
                if 'device' in available_viz:
                    with tabs[tab_idx]:
                        device_metric = st.selectbox(
                            "Select metric for device analysis", 
                            options=available_viz['device']['metrics'],
                            key="device_metric"
                        )
                        fig = create_top_performers_chart(processed_df, 'device', device_metric, 'bar', 8)
                        st.plotly_chart(fig, use_container_width=True)
                    tab_idx += 1
                
                # Browser performance
                if 'browser' in available_viz:
                    with tabs[tab_idx]:
                        browser_metric = st.selectbox(
                            "Select metric for browser analysis", 
                            options=available_viz['browser']['metrics'],
                            key="browser_metric"
                        )
                        fig = create_top_performers_chart(processed_df, 'browser', browser_metric, 'bar', 8)
                        st.plotly_chart(fig, use_container_width=True)
                    tab_idx += 1
                
                # Correlation heatmap
                if 'correlation' in available_viz:
                    with tabs[tab_idx]:
                        fig = create_correlation_heatmap(processed_df)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Not enough numeric data for correlation analysis.")
            else:
                st.info("No visualizations available with the current data.")
            
            # Download insights as text
            if insights and isinstance(insights, list) and len(insights) > 0:
                insights_text = "\n".join([f"{i+1}. {insight}" for i, insight in enumerate(insights) if insight and len(insight) > 10])
                st.download_button(
                    label="Download Insights as Text",
                    data=insights_text,
                    file_name="marketing_insights.txt",
                    mime="text/plain"
                )
            
            else:
                        st.error("❌ Data validation failed. The uploaded file doesn't contain sufficient marketing data.")
                        # UPDATED: Changed from 3 metrics and 2 dimensions to 1 metric and 1 dimension
                        st.write("**Required metrics at minimum:** 1 of ['spend', 'cost', 'cpc', 'ctr', 'roi', 'transactions', 'conversions', 'revenue']")
                        st.write("**Required dimensions at minimum:** 1 of ['campaign', 'source', 'medium', 'date', 'city', 'state', 'age', 'gender', 'device', 'browser']")
                        
                        # Show what was detected
                        st.info("**Detected in your data:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Metrics found:", validation_result["available_metrics"])
                        with col2:
                            st.write("Dimensions found:", validation_result["available_dimensions"])
    
    except Exception as e:
        st.error(f"Error during data processing: {str(e)}")
        st.write("Please check your data format and try again.")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

else:
    # Show instructions when no file is uploaded
    st.info("👈 Please upload a CSV or Excel file using the sidebar, or check 'Use sample data' to try with demo data.")
    
    # Sample data structure guidance
with st.expander("What should my data structure look like?"):
        st.markdown("""
        Your marketing data should include these metrics and dimensions:
        
        **Metrics (include at least 1):**
        - spend: Total advertising spend
        - cost: Cost associated with campaigns
        - cpc: Cost per click
        - ctr: Click-through rate
        - roi: Return on investment
        - transactions: Number of transactions
        - conversions: Number of conversions
        - revenue: Total revenue generated
        
        **Dimensions (include at least 1):**
        - date: Date of activity
        - campaign: Campaign name
        - source: Traffic source (Google, Facebook, etc.)
        - medium: Marketing medium (CPC, Social, etc.)
        - city: City of origin
        - state: State of origin
        - age: User age group
        - gender: User gender
        - device: User device type
        - browser: User browser type
        
        *Note: The more data you provide, the better insights you'll get!*
        """)
        
        # Show sample data
        sample_df = generate_sample_data()
        st.write("Sample data structure:")
        st.dataframe(sample_df.head(10))
        
        # Download sample data
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="Download Sample Data (CSV)",
            data=csv,
            file_name="sample_marketing_data.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>"
    "Marketing Insight Generator • Multi-Agent System • Powered by Streamlit & OpenAI"
    "</div>",
    unsafe_allow_html=True
)