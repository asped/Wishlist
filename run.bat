@echo off

REM Family Gift List - Quick Start Script for Windows

echo.
echo 🎁 Starting Family Gift List...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start the application
echo ✅ Starting the web server...
echo.
echo 🌐 Open your browser and go to:
echo    http://localhost:5000
echo.
echo 📝 Admin Dashboard: http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
