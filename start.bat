@echo off
REM ========================================
REM MacQuiz - Complete Setup (Windows)
REM ========================================

color 0A
cls

echo ========================================
echo      MacQuiz - Complete Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not installed
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js 16 or higher from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found
node --version
echo.

REM ========================================
REM Backend Setup
REM ========================================
echo ========================================
echo   Setting up Backend
echo ========================================
echo.

cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed

REM Start backend server in new window
echo Starting backend server...
start "MacQuiz Backend" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo [OK] Backend server started in new window
echo    URL: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.

cd ..

REM ========================================
REM Frontend Setup
REM ========================================
echo ========================================
echo   Setting up Frontend
echo ========================================
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed
) else (
    echo [OK] Frontend dependencies already installed
)

REM Start frontend server in new window
echo Starting frontend server...
start "MacQuiz Frontend" cmd /k "cd /d %CD% && npm run dev"
echo [OK] Frontend server started in new window
echo    URL: http://localhost:5173
echo.

cd ..

REM ========================================
REM Summary
REM ========================================
timeout /t 3 /nobreak >nul

echo ========================================
echo   MacQuiz is Running!
echo ========================================
echo.
echo Frontend:    http://localhost:5173
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo.
echo Default Login Credentials:
echo   Email:    admin@macquiz.com
echo   Password: admin123
echo.
echo Two new command windows have been opened:
echo   1. MacQuiz Backend  (Backend server)
echo   2. MacQuiz Frontend (Frontend server)
echo.
echo To stop all servers, close both command windows
echo or use the stop.bat script.
echo.
echo Press any key to exit this setup window...
pause >nul
