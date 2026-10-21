@echo off
title Email Spam Pattern Detector

:: Navigate to the directory where this script is located
cd /d "%~dp0"

echo ======================================================================
echo          Email Spam Pattern Detector - Automata TOC Project
echo ======================================================================
echo.

:: 1. Check if Python is installed and accessible in PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected:
python --version
echo.

:: 2. Detect and activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: venv
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: .venv
    call ".venv\Scripts\activate.bat"
) else (
    echo [INFO] No local venv found. Using active Python environment.
)
echo.

:: 3. Verify Streamlit dependency and install requirements if needed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Streamlit is not installed in the active environment.
    echo [INFO] Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies from requirements.txt.
        echo Please check your internet connection or run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully.
    echo.
)

:: 4. Launch the Streamlit application
echo ======================================================================
echo  Launching Streamlit Web Application...
echo  Local URL: http://localhost:8501
echo  Press Ctrl+C in this console window to stop the server.
echo ======================================================================
echo.

python -m streamlit run app.py

:: 5. Keep window open if application stops or encounters an issue
if errorlevel 1 (
    echo.
    echo [ERROR] The application stopped unexpectedly with an error code.
)
echo.
echo Application stopped. Press any key to exit...
pause >nul
