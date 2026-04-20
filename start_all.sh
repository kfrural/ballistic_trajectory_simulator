#!/bin/bash
# Quick start for Ballistic Trajectory Simulator
cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator

# Load env vars
export APP_ENV=test
export DATABASE_URL=sqlite:///ballistic.db

echo "==================================="
echo "BALLISTIC TRAJECTORY SIMULATOR"
echo "==================================="

# API
echo "[1] Starting FastAPI..."
source venv/bin/activate
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

# Wait and check
sleep 3
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "    ✓ API: http://127.0.0.1:8000"
fi

# Frontend
echo "[2] Starting React..."
cd frontend
npm start &
FE_PID=$!

cd ..

echo ""
echo "==================================="
echo "DONE!"
echo "  - API:      http://127.0.0.1:8000"
echo "  - Docs:     http://127.0.0.1:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo "==================================="

trap "kill $API_PID $FE_PID 2>/dev/null" EXIT
wait