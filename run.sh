#!/bin/bash

echo "======================================"
echo "T20 World Cup 2026 Analytics System"
echo "======================================"
echo ""

# Check if models exist
if [ ! -f "models/match_predictor.pkl" ] || [ ! -f "models/score_predictor.pkl" ]; then
    echo "⚠️  Models not found. Training models first..."
    python train_models.py
    echo ""
fi

echo "🚀 Starting Streamlit Dashboard..."
echo ""
echo "📱 Access the dashboard at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py --server.port 8501 --server.address 0.0.0.0
