#!/bin/bash
set -e

# Render assigns the port via $PORT; fall back to 10000 for local testing
PORT=${PORT:-10000}

echo "Starting FastAPI on internal port 8000..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Wait for backend to be ready
sleep 5

echo "Starting Streamlit on port $PORT..."
streamlit run app/ui.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false