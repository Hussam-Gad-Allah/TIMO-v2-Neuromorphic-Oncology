#!/usr/bin/env bash
# TIMO v2 : Turnkey Linux/macOS Launcher
cd "$(dirname "$0")"

echo "========================================================================"
echo "      TIMO v2 : Biological Connectome Neuromorphic Computing Engine     "
echo "      3D Drosophila Flight Simulator & Pan-Cancer Precision Solver      "
echo "========================================================================"

if [ -f ".venv/bin/activate" ]; then
    echo "[*] Activating local environment (.venv)..."
    source .venv/bin/activate
else
    if ! command -v python3 &> /dev/null; then
        echo "[!] Python 3 could not be found. Please install Python 3.10+."
        exit 1
    fi
    echo "[*] First-time setup: creating isolated .venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
fi

python3 launcher.py
