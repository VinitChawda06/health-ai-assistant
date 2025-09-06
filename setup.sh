#!/bin/bash
# Universal setup script for health-ai-assistant
# Works on Linux, macOS, and Windows (via Git Bash/WSL)

set -e

echo "🚀 Health AI Assistant - Universal Setup Script"
echo "=============================================="

# Detect OS
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
fi

echo "📋 Detected OS: $OS"

# Check dependencies
echo "🔍 Checking dependencies..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found! Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "✅ Python version: $PYTHON_VERSION"

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip not found! Please install pip"
    exit 1
fi

echo "✅ pip available"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo "✅ Docker available"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker not found (optional for containerized deployment)"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "🔧 Setting up virtual environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OS" == "Windows" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"

# Upgrade pip
$PIP_CMD install --upgrade pip

echo ""
echo "📦 Installing backend dependencies..."
cd backend
$PIP_CMD install -r requirements.txt
cd ..

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
$PIP_CMD install -r requirements.txt
cd ..

echo ""
echo "🔍 Verifying data files..."
if [ -f "data/videos.json" ] && [ -f "data/merged.json" ]; then
    echo "✅ Data files found"
else
    echo "⚠️  Data files not found in data/ directory"
    echo "   Please ensure videos.json and merged.json are in the data/ folder"
fi

echo ""
echo "🧪 Testing backend..."
cd backend
timeout 10s $PYTHON_CMD -c "
import sys
sys.path.append('.')
try:
    from main import app
    print('✅ Backend imports successfully')
except ImportError as e:
    print(f'❌ Backend import failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'⚠️  Backend warning: {e}')
" || echo "⚠️  Backend test timed out (may be loading data)"
cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Quick Start Commands:"
echo "========================"
echo ""
echo "1. Run backend (in one terminal):"
if [[ "$OS" == "Windows" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   cd backend"
echo "   python main.py"
echo ""
echo "2. Run frontend (in another terminal):"
if [[ "$OS" == "Windows" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   cd frontend"
echo "   streamlit run app.py"
echo ""
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "3. Or run with Docker:"
    echo "   docker-compose up --build"
    echo ""
fi
echo "🌐 Access the app at: http://localhost:8501"
echo ""
echo "📚 For troubleshooting, check README.md"
