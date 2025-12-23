#!/bin/bash

# Art Frame API Startup Script

echo "🖼️  Starting Art Frame API..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the art_frame_api directory."
    exit 1
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p storage/frames
mkdir -p storage/uploads  
mkdir -p storage/results
mkdir -p database

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -r ../requirements.txt

# Start the API server
echo "🚀 Starting server on http://localhost:8000"
echo "📊 Management interface: http://localhost:8000/frames/manage"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000