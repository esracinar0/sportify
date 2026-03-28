@echo off
REM Django Ecommerce Project - Windows Batch Runner
REM This script sets up and runs the Django development server

setlocal enabledelayedexpansion

echo.
echo ============================================
echo Django Ecommerce Project Launcher
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version
echo.

REM Check if venv exists, if not create it
if not exist "venv\" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)
echo.

REM Install/update dependencies
echo [4/4] Installing dependencies...
pip install -q -r ecommerce\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo.

REM Run migrations
echo Running database migrations...
cd ecommerce
python manage.py migrate --noinput
cd ..
echo.

REM Start the development server
echo.
echo ============================================
echo Starting Django Development Server
echo ============================================
echo Open your browser at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo ============================================
echo.

cd ecommerce
python manage.py runserver
pause
