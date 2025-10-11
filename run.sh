#!/bin/bash

# Family Gift List - Quick Start Script

echo "🎁 Starting Family Gift List..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Start the application
echo "✅ Starting the web server..."
echo ""
echo "🌐 Open your browser and go to:"
echo "   http://localhost:5000"
echo ""
echo "📝 Admin Dashboard: http://localhost:5000/admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
