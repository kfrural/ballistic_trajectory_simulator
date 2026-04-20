#!/bin/bash
# Simpler start script for just the Airflow web UI

cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow_home

echo "====================================="
echo "STARTING AIRFLOW UI"
echo "====================================="

# Copy dags
mkdir -p $AIRFLOW_HOME/dags
cp dags/*.py $AIRFLOW_HOME/dags/

# Just the api-server
airflow api-server -p 8080 &
API_PID=$!

sleep 5

echo ""
echo "====================================="
echo "Airflow UI starting..."
echo "  URL: http://localhost:8080"
echo "  User: admin"
echo "  Password: check airflow_home/*.json.generated"
echo "====================================="

wait