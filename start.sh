#!/bin/bash

echo "🎬 Video Analyzer AI - Startup Script"
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12.7 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
REQUIRED_VERSION="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python $PYTHON_VERSION found (compatible with Python 3.12.7)"
else
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.8 or higher."
    echo "   Recommended: Python 3.12.7"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists and has API key
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please set your OpenAI API key in the .env file"
    echo "   Edit .env and replace 'your_openai_api_key_here' with your actual API key"
    exit 1
fi

echo "✅ Environment configured"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Video processing may not work."
    echo "   Install FFmpeg:"
    echo "   - Mac: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/"
else
    echo "✅ FFmpeg found"
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "🚀 Starting Video Analyzer AI..."
echo ""
echo "Backend will start on: http://localhost:8000"
echo "Frontend will start on: http://localhost:3000"
echo ""
echo "To start:"
echo "1. Backend: python3 run_backend.py"
echo "2. Frontend: python3 run_frontend.py (in a new terminal)"
echo ""
echo "Or run both automatically:"
echo "python3 run_backend.py &"
echo "python3 run_frontend.py"