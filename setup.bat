@echo off
REM Universal setup script for health-ai-assistant on Windows
REM Works with PowerShell, Command Prompt, and Git Bash

echo 🚀 Health AI Assistant - Windows Setup Script
echo ==============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found! Please install pip
    pause
    exit /b 1
)

echo ✅ pip available

REM Check Docker (optional)
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not found (optional for containerized deployment)
    set DOCKER_AVAILABLE=false
) else (
    echo ✅ Docker available
    set DOCKER_AVAILABLE=true
)

echo.
echo 🔧 Setting up virtual environment...

REM Create virtual environment
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
pip install --upgrade pip

echo.
echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo 📦 Installing frontend dependencies...
cd frontend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo 🔍 Verifying data files...
if exist "data\videos.json" (
    if exist "data\merged.json" (
        echo ✅ Data files found
    ) else (
        echo ⚠️  merged.json not found in data\ directory
    )
) else (
    echo ⚠️  videos.json not found in data\ directory
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 🚀 Quick Start Commands:
echo ========================
echo.
echo 1. Run backend (in one terminal):
echo    venv\Scripts\activate.bat
echo    cd backend
echo    python main.py
echo.
echo 2. Run frontend (in another terminal):
echo    venv\Scripts\activate.bat
echo    cd frontend
echo    streamlit run app.py
echo.
if "%DOCKER_AVAILABLE%"=="true" (
    echo 3. Or run with Docker:
    echo    docker-compose up --build
    echo.
)
echo 🌐 Access the app at: http://localhost:8501
echo.
echo 📚 For troubleshooting, check README.md
echo.
pause
