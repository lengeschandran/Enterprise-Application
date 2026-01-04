@echo off
TITLE OCR Monitor Launcher

:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

echo ==================================================
echo       Starting OCR Monitor 
echo ==================================================
echo.


:: FIND PYTHON

:: Priority 1: Check for local virtual environment 'xp_env'
if exist "%~dp0xp_env\Scripts\python.exe" (
    set PYCMD="%~dp0xp_env\Scripts\python.exe"
) else if exist "C:\Python34\python.exe" (
    set PYCMD="C:\Python34\python.exe"
) else if exist "C:\Program Files\Python34\python.exe" (
    set PYCMD="C:\Program Files\Python34\python.exe"
) else if exist "C:\Program Files (x86)\Python34\python.exe" (
    set PYCMD="C:\Program Files (x86)\Python34\python.exe"
) else (
    :: Fallback: assume it's in the PATH
    set PYCMD=python
)

echo Using interpreter: %PYCMD%
echo.

:: Run the script using the found command
%PYCMD% ocr.py

:: Check if it failed
if %errorlevel% NEQ 0 (
    echo.
    echo ==================================================
    echo [ERROR] Could not run the script.
    echo.
    echo Troubleshooting:
    echo 1. Ensure 'xp_env' is in the same folder as this file.
    echo 2. Ensure 'ocr.py' is in the same folder.
    echo 3. If using a global install, ensure Python 3.4 is installed.
    echo ==================================================
)

echo.
echo --------------------------------------------------
echo Script execution finished.

pause
