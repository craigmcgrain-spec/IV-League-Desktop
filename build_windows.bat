@echo off
setlocal enabledelayedexpansion
REM Build Windows .exe for IV League Desktop
REM Run this on Windows with Python 3.10+ installed

set APP_NAME=IVLeague
set VERSION=1.0.0

echo ============================================
echo  IV League Desktop v%VERSION% - Windows Build
echo ============================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install pyinstaller PyQt6 reportlab
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name %APP_NAME% ^
    --icon iv_league\assets\icon.ico ^
    --add-data "iv_league\assets;iv_league\assets" ^
    --add-data "iv_league\database;iv_league\database" ^
    --clean ^
    main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo ============================================
echo  Output: dist\%APP_NAME%.exe
echo ============================================
echo.
echo To create an installer:
echo   1. Download Inno Setup from https://jrsoftware.org/isinfo.php
echo   2. Open installer\iv-league-setup.iss
echo   3. Click Build ^> Compile
echo.
echo Or distribute dist\%APP_NAME%.exe directly (no installer needed).
echo.
pause
