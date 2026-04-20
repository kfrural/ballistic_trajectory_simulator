#!/bin/bash
# Script to start all services for development

echo "Starting Ballistic Trajectory Simulator..."
echo ""

# Start backend in background
cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator
source venv/bin/activate
echo "[1] Starting FastAPI backend on port 8000..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator/frontend
echo "[2] Starting React frontend on port 3000..."
PORT=3000 npm start &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "Services started:"
echo "  - Frontend: http://localhost:3000"
echo "  - API:       http://localhost:8000"
echo "  - Docs:      http://localhost:8000/docs"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup EXIT INT TERM

wait