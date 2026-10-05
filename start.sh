#!/bin/bash
set -e

# Use Render's PORT env var, default to 7860 for local testing
PORT=${PORT:-7860}

# Start FastAPI backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend
sleep 5

# Start Streamlit on the assigned port
streamlit run app/ui.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false