#!/bin/bash
# Production startup script for Wishlist App

echo "🚀 Starting Wishlist App in Production Mode"
echo "============================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ Created .env file from template"
        echo "🔧 Please edit .env file with your production settings"
        echo "   Run: python setup_env.py create"
        exit 1
    else
        echo "❌ env.template not found!"
        exit 1
    fi
fi

# Check if virtual environment exists
#if [ ! -d "venv" ]; then
#    echo "📦 Creating virtual environment..."
#    python3 -m venv venv
#fi

# Activate virtual environment
#echo "🔧 Activating virtual environment..."
#source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔍 Checking environment configuration..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['SECRET_KEY', 'BREVO_API_KEY', 'BREVO_SENDER_EMAIL']
missing_vars = []

for var in required_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Missing required environment variables: {missing_vars}')
    print('📝 Please configure these in your .env file')
    exit(1)
else:
    print('✅ Environment configuration looks good!')
"

if [ $? -ne 0 ]; then
    echo "❌ Environment configuration incomplete"
    exit 1
fi

echo "Setup completed"

# Start the application
#echo "🌟 Starting Flask application..."
#echo "🌐 App will be available at: http://0.0.0.0:5000"
#echo "🛑 Press Ctrl+C to stop"
#echo ""

#python app.py
