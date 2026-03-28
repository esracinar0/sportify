@echo off
REM Django Ecommerce Project - Setup Only
REM This script only sets up the environment without running the server

setlocal enabledelayedexpansion

echo.
echo ============================================
echo Django Ecommerce Project Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

REM Check if venv exists, if not create it
if not exist "venv\" (
    echo [2/3] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/3] Virtual environment already exists.
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/3] Installing dependencies...
pip install -q -r ecommerce\requirements.txt
echo.

echo Setup complete! 
echo To start the server, run: run.bat
echo Or use: cd ecommerce && python manage.py runserver
pause
