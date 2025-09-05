#!/bin/bash

echo "🚀 Starting FastAPI Backend..."

# Activate virtual environment
source health_ai_env/bin/activate

# Change to backend directory
cd backend

# Start FastAPI server
echo "Starting server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
