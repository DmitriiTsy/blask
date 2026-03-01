#!/bin/bash

# Script to run Blask project

echo "🚀 Starting Blask project..."

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

# Run the project
echo "▶️  Running Blask..."
echo ""
echo "💡 Tip: You can pass query as argument:"
echo "   python3 -m src.main 'your query here'"
echo ""

# Pass all arguments to main script
python3 -m src.main "$@"
