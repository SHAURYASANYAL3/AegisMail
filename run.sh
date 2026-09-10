#!/bin/bash
set -e

echo "============================================================"
echo "AEGISMAIL — AI Email Digital Forensics & Threat Intelligence"
echo "SIH26106 | 100% Offline Capable | Zero-API Key Requirement"
echo "============================================================"

# Check Python virtualenv
if [ ! -d ".venv" ]; then
    echo "[!] .venv not found. Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

# Check frontend node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo "[!] frontend/node_modules not found. Installing..."
    cd frontend && npm install && cd ..
fi

echo "[*] Starting FastAPI Backend on http://127.0.0.1:8000 ..."
PYTHONPATH=. .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "[*] Starting Vite Frontend on http://localhost:5173 ..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo '[*] AegisMail stopped cleanly.'" SIGINT SIGTERM EXIT

echo "============================================================"
echo "[+] AEGISMAIL PLATFORM ACTIVE"
echo "    Frontend: http://localhost:5173"
echo "    Backend API: http://127.0.0.1:8000"
echo "    API Documentation: http://127.0.0.1:8000/docs"
echo "============================================================"

wait
