#!/bin/bash
# run.sh - KitForge startup script

echo "🔧 Starting KitForge..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create directories
mkdir -p uploads output

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Backend API:  cd backend/api && python main.py"
echo "  2. Frontend:     streamlit run frontend/app.py"
echo ""
