#!/bin/bash

# Huberman Health AI Assistant Setup Script

echo "🧠 Setting up Huberman Health AI Assistant..."

# Create virtual environment if it doesn't exist
if [ ! -d "health_ai_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv health_ai_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source health_ai_env/bin/activate

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenRouter API key"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenRouter API key"
echo "2. Run: ./run_backend.sh (in one terminal)"
echo "3. Run: ./run_frontend.sh (in another terminal)"
echo "4. Open http://localhost:8501 in your browser"
