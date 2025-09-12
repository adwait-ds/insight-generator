# Multi-Agent Insight Generator (Streamlit) <br>
This repo is a runnable Streamlit app that demonstrates a two-agent workflow:<br>
Agent 1 (Data Intake & Validation): Reads uploaded CSV/XLSX or extracts table from PNG/JPG via OCR, infers column types, maps metrics/dimensions and validates sufficiency.<br>
Agent 2 (Insight Generator): Computes aggregated metrics, highlights top/bottom segments, detects anomalies, computes derived KPIs and produces structured insights (Good points, Areas for improvement, Suggestions, Issues).<br>
Features:<br>
LLM integration (OpenAI-compatible) for human-readable insight text<br>
Visualizations (bar charts, time series if date present)<br>
Interactive column mapping and re-run loop when data insufficient<br>
Downloadable insights JSON
