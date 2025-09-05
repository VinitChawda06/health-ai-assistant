#!/bin/bash

echo "🎨 Starting Streamlit Frontend..."

# Activate virtual environment
source health_ai_env/bin/activate

# Change to frontend directory
cd frontend

# Start Streamlit app
echo "Starting Streamlit on http://localhost:8501"
streamlit run app.py --server.port 8501
