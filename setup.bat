@echo off
title Username Checker - Setup
color 0B

echo ========================================
echo        Username Checker - Setup
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python found.
echo.

echo [2/3] Installing requirements from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Something went wrong while installing dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Dependencies installed successfully.
echo.
echo Starting Username Checker...
echo.

python username_checker.py

pause
