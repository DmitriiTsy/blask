#!/bin/bash

# Script to run Blask web application

echo "🌐 Starting Blask Web Application..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Using system Python."
    echo "   To create venv: python3 -m venv venv"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   Please edit .env and add your API keys"
    else
        echo "   .env.example not found. You may need to create .env manually"
    fi
fi

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📥 Installing Streamlit..."
    pip install streamlit
fi

# Run Streamlit app
echo "▶️  Starting web server..."
echo ""
echo "🌐 Web interface will open at: http://localhost:8501"
echo ""

# Set PYTHONPATH to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run from project root to ensure imports work
cd "$(dirname "$0")"
streamlit run src/webapp.py
