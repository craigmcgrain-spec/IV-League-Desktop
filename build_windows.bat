@echo off
REM Build Windows .exe for IV League Desktop
REM Run this on Windows with Python 3.10+ installed

echo Installing dependencies...
pip install pyinstaller PyQt6 reportlab

echo Building IV League Desktop...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name IVLeague ^
    --add-data "iv_league\assets;iv_league\assets" ^
    --add-data "iv_league\database;iv_league\database" ^
    --clean ^
    main.py

echo.
echo Done! Created dist\IVLeague.exe
echo.
echo To create an installer:
echo 1. Download Inno Setup from https://jrsoftware.org/isinfo.php
echo 2. Open installer\iv-league-setup.iss
echo 3. Click Build > Compile
echo.
pause
