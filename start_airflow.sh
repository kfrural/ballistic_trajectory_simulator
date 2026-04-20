#!/bin/bash
# Start Airflow properly

cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator

echo "====================================="
echo "STARTING APACHE AIRFLOW"
echo "====================================="

# Activate venv
source venv/bin/activate

# Set Airflow home
export AIRFLOW_HOME=/home/kfrural/Documentos/github/ballistic_trajectory_simulator/airflow_home

# Copy DAGs if needed
mkdir -p $AIRFLOW_HOME/dags
cp dags/*.py $AIRFLOW_HOME/dags/ 2>/dev/null

# Start standalone (includes webserver + scheduler + triggerer)
echo "Starting Airflow standalone..."
echo ""
echo "Login info:"
echo "  URL: http://localhost:8080"
echo "  User: admin"

if [ -f "$AIRFLOW_HOME/simple_auth_manager_passwords.json.generated" ]; then
    echo "  Password: $(cat $AIRFLOW_HOME/simple_auth_manager_passwords.json.generated | grep -o 'admin.*' | cut -d'"' -f4)"
fi

echo ""
echo "====================================="

# Run in foreground
airflow standalone