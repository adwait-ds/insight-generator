# Multi-Agent Insight Generator (Streamlit)
This repo is a runnable Streamlit app that demonstrates a two-agent workflow:
Agent 1 (Data Intake & Validation): Reads uploaded CSV/XLSX or extracts table from PNG/JPG via OCR, infers column types, maps metrics/dimensions and validates sufficiency.
Agent 2 (Insight Generator): Computes aggregated metrics, highlights top/bottom segments, detects anomalies, computes derived KPIs and produces structured insights (Good points, Areas for improvement, Suggestions, Issues).
Features:
LLM integration (OpenAI-compatible) for human-readable insight text
Visualizations (bar charts, time series if date present)
Interactive column mapping and re-run loop when data insufficient
Downloadable insights JSON
Requirements
Python 3.9+
See requirements.txt
Installation
Clone repo and cd into folder
Create virtualenv and install:
pip install -r requirements.txt
Set environment variable:
export OPENAI_API_KEY="sk-..."   (or set in your OS)
Run:
streamlit run app.py
Notes
For OCR on images, this uses pytesseract. Make sure Tesseract is installed on your system.
The LLM calls are minimal. The prompt instructs the LLM to only use provided computed values — not to invent numbers.
