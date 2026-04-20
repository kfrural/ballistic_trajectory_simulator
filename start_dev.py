#!/usr/bin/env python3
"""Quick start script for Ballistic Trajectory Simulator."""

import os
import sys
import subprocess
import time
import signal

os.chdir("/home/kfrural/Documentos/github/ballistic_trajectory_simulator")

# Load env
os.environ.setdefault("APP_ENV", "test")
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

print("=" * 50)
print("BALLISTIC TRAJECTORY SIMULATOR")
print("=" * 50)
print()

# Start API
print("[1] Starting FastAPI on port 8000...")
api_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
time.sleep(3)

# Check API
try:
    import urllib.request
    urllib.request.urlopen("http://127.0.0.1:8000/", timeout=2)
    print("    ✓ API running at http://127.0.0.1:8000")
except:
    print("    ⚠ API starting...")

# Start Frontend
print("[2] Starting React on port 3000...")
fe_proc = subprocess.Popen(
    ["npm", "start"],
    cwd="./frontend",
    env={**os.environ, "PORT": "3000"},
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

print()
print("=" * 50)
print("READY!")
print("  - API:      http://127.0.0.1:8000")
print("  - Docs:     http://127.0.0.1:8000/docs")
print("  - Frontend: http://localhost:3000")
print("=" * 50)
print()
print("Press Ctrl+C to stop all services")

def cleanup(sig, frame):
    print("\nStopping services...")
    api_proc.terminate()
    fe_proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup(None, None)
