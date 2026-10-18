@echo off
title TIMO v2 : Biological Connectome Neuromorphic Engine
cd /d "%~dp0"

echo ========================================================================
echo       TIMO v2 : Biological Connectome Neuromorphic Computing Engine
echo       3D Drosophila Flight Simulator ^& Pan-Cancer Precision Solver
echo ========================================================================
echo.

:: 1. Check if local .venv already exists
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating isolated local environment (.venv)...
    call .venv\Scripts\activate.bat
    goto :LAUNCH
)

:: 2. Check if global Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python was not found on your system PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 3. Automatically bootstrap local .venv if missing
echo [*] First-time setup detected. Bootstrapping isolated environment...
echo [*] Creating local .venv (this only happens once)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [!] Failed to create local .venv. Running with system Python...
    goto :SYSTEM_RUN
)

call .venv\Scripts\activate.bat
echo [*] Installing required packages (PyTorch, NumPy, SciPy)...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
echo [*] Environment ready!

:LAUNCH
python launcher.py
goto :END

:SYSTEM_RUN
python launcher.py

:END
pause
