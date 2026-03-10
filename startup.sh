#!/bin/bash
# Azure App Service startup command for Streamlit
# Azure injects $PORT automatically (usually 8000)

set -e

echo "[startup] Starting AI Research Agent..."
echo "[startup] PORT=${PORT:-8000}"

exec streamlit run app.py \
    --server.port="${PORT:-8000}" \
    --server.address="0.0.0.0" \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.fileWatcherType=none