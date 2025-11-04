#!/bin/bash
# Startup script for Image-to-Code Generation Service

set -e

echo "🚀 Starting Image-to-Code Generation Service"
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Check which service to run
SERVICE=${1:-both}

if [ "$SERVICE" == "api" ]; then
    echo "📡 Starting FastAPI service..."
    python image_to_code_service.py
elif [ "$SERVICE" == "gradio" ]; then
    echo "🎨 Starting Gradio interface..."
    python gradio_interface.py
else
    echo "📡 Starting FastAPI service in background..."
    python image_to_code_service.py &
    API_PID=$!
    
    echo "⏳ Waiting for API to start..."
    sleep 3
    
    echo "🎨 Starting Gradio interface..."
    python gradio_interface.py
    
    # Cleanup on exit
    trap "kill $API_PID" EXIT
fi
