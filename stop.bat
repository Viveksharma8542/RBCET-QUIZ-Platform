@echo off
REM ========================================
REM MacQuiz - Stop All Servers (Windows)
REM ========================================

color 0C
cls

echo ========================================
echo   MacQuiz - Stopping Servers
echo ========================================
echo.

echo Stopping backend server (uvicorn)...
taskkill /FI "WINDOWTITLE eq MacQuiz Backend*" /F >nul 2>&1
taskkill /IM python.exe /FI "MEMUSAGE gt 20000" /F >nul 2>&1

echo Stopping frontend server (npm/node)...
taskkill /FI "WINDOWTITLE eq MacQuiz Frontend*" /F >nul 2>&1

echo.
echo [OK] All servers stopped
echo.
pause
