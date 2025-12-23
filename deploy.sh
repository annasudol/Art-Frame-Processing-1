#!/bin/bash

# Deployment script for Art Frame Processing Tool
# Usage: ./deploy.sh

set -e  # Exit on any error

# Variables
REPO_URL="https://github.com/oyekamal/Automated-Art-Frame-Processing-Tool.git"
APP_DIR="$HOME/art-work"
PYTHON_VERSION="python3"
VENV_DIR="$APP_DIR/venv"

echo "🚀 Starting deployment..."

# Update system packages
echo "📦 Updating system packages..."
apt update
apt install -y $PYTHON_VERSION python3-pip python3-venv git curl \
    libgl1-mesa-dri libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    libgomp1 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 \
    python3-opencv libopencv-dev ffmpeg libavcodec-extra

# Create app directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    echo "📁 Creating application directory..."
    mkdir -p "$APP_DIR"
fi

cd "$APP_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    echo "🔄 Updating existing repository..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" .
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    $PYTHON_VERSION -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make start script executable
echo "🔒 Making start script executable..."
cd art_frame_api
chmod +x start_api.sh

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Killing existing process..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

echo "🎯 Starting the API server..."
echo "📍 Server will be available at: http://163.172.167.251:8000"
echo "📝 API documentation at: http://163.172.167.251:8000/docs"

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Start the server in background
nohup ./start_api.sh > ../logs/server.log 2>&1 &
SERVER_PID=$!

echo "✅ Deployment completed!"
echo "🆔 Server PID: $SERVER_PID"
echo "📋 To check logs: tail -f $APP_DIR/logs/server.log"
echo "🛑 To stop server: pkill -f 'python.*main.py'"

# Deactivate virtual environment
deactivate