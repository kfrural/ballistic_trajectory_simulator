# Ballistic Trajectory Simulator - Technical Specification

## 1. Project Overview

**Project Name**: BallisticTrajectorySimulator
**Type**: Full-stack Data Engineering + ML + Physics Simulation Platform

A sophisticated ballistic trajectory simulator that combines:
- **ETL Pipelines**: Weather data (OpenWeatherMap) + Topography (OSM/Overpass)
- **Physics Engine**: Numpy-based trajectory calculations with air resistance, Coriolis effect, wind
- **ML Optimization**: Gemini AI for parameter optimization (fire solutions)
- **Orchestration**: Apache Airflow for pipeline management
- **Frontend**: React + visualization
- **Backend**: FastAPI for real-time calculations

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│   React Frontend (Charts/3D) ←→ FastAPI Backend                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                         │
│              Apache Airflow (DAGs, Scheduling)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       PROCESSING LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │ ETL Weather │  │ ETL Topo    │  │ Physics Engine (Numpy)  ││
│  │ (OpenAPI)   │  │ (OSM)       │  │ + Gemini Optimizer       ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│     PostgreSQL ( trajectories, params ) + Redis (cache)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI |
| Physics Engine | NumPy, SciPy |
| ML/AI | Google Gemini API |
| Orchestration | Apache Airflow 2.x |
| Database | PostgreSQL + Redis |
| Container | Docker + Docker Compose |
| Weather API | OpenWeatherMap |
| Topography | OSM/Overpass API |
| Frontend | React + TypeScript + Chart.js |

---

## 4. Core Modules

### 4.1 ETL Weather Module (`src/etl/weather`)
- Fetches weather data from OpenWeatherMap API
- Extracts: temperature, pressure, humidity, wind speed/direction
- Transforms to atmospheric density model
- Loads to PostgreSQL with timestamp

### 4.2 ETL Topography Module (`src/etl/topography`)
- Fetches elevation data from OSM/Overpass API
- Generates Digital Terrain Model (DTM)
- Calculates line-of-sight, slope effects
- Caches results in Redis

### 4.3 Physics Engine (`src/physics`)
- **Basic**: Simple ballistic equations (no drag)
- **Advanced**: 
  - Air resistance (drag coefficient)
  - Wind correction (crosswind, headwind)
  - Coriolis effect (Earth rotation)
  - humidity and temperature effects
  - Atmospheric density variation with altitude
- Integration methods: Euler, Runge-Kutta 4th order

### 4.4 Gemini Optimizer (`src/optimizer`)
- Input: Target coordinates, constraints
- Output: Optimal fire parameters (elevation, azimuth, charge)
- Uses Gemini 2.0 API for intelligent search
- Considers weather and terrain in real-time

### 4.5 Airflow DAGs (`dags/`)
- `dag_weather_etl`: Daily weather ingestion
- `dag_topography_etl`: On-demand terrain fetch
- `dag_trajectory_batch`: Batch trajectory calculations
- `dag_optimization`: Parameter optimization workflow

---

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/simulate` | Run single trajectory |
| POST | `/api/v1/optimize` | Get optimal fire parameters |
| GET | `/api/v1/weather/{lat}/{lon}` | Get weather data |
| GET | `/api/v1/terrain/{lat}/{lon}` | Get terrain elevation |
| GET | `/api/v1/trajectories` | List saved trajectories |
| GET | `/api/v1/health` | Health check |

---

## 6. Physics Equations

### 6.1 Basic Trajectory (No Drag)
```
x(t) = v₀ * cos(θ) * t
y(t) = v₀ * sin(θ) * t - 0.5 * g * t²
```

### 6.2 With Air Resistance
```
dx/dt = -k * v * vx
dy/dt = g - k * v * vy
```

### 6.3 Coriolis Effect
```
F_coriolis = 2 * m * Ω × v
```

---

## 7. Data Models

### 7.1 Trajectory
```python
{
    "id": "uuid",
    "projectile_type": "mortar_81mm",
    "initial_velocity": 250.0,  # m/s
    "elevation_angle": 45.0,   # degrees
    "azimuth": 180.0,           # degrees (from North)
    "weather_id": "uuid",
    "trajectory_points": [...],
    "max_range": 4500.0,
    "max_altitude": 1200.0,
    "flight_time": 45.2,
    "created_at": "timestamp"
}
```

### 7.2 Weather
```python
{
    "id": "uuid",
    "lat": -23.5505,
    "lon": -46.6333,
    "temperature": 25.0,        # Celsius
    "pressure": 1013.25,        # hPa
    "humidity": 65,             # %
    "wind_speed": 5.0,          # m/s
    "wind_direction": 180,      # degrees
    "density": 1.184,           # kg/m³
    "timestamp": "datetime"
}
```

---

## 8. Deployment

### Docker Compose Services
1. **postgres**: PostgreSQL 15
2. **redis**: Redis 7 (cache)
3. **airflow-webserver**: Airflow UI
4. **airflow-scheduler**: Airflow scheduler
5. **airflow-worker**: Celery worker
6. **fastapi**: Backend API
7. **frontend**: React app (nginx)

---

## 9. Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Docker
docker-compose up -d

# Or run locally
# Terminal 1: airflow webserver
# Terminal 2: airflow scheduler
# Terminal 3: uvicorn app.main:app
```

---

## 10. Project Structure

```
ballistic_trajectory_simulator/
├── dags/                    # Airflow DAGs
│   ├── __init__.py
│   ├── dag_weather_etl.py
│   ├── dag_topography_etl.py
│   ├── dag_trajectory.py
│   └── dag_optimization.py
├── src/
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── weather/
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py
│   │   │   ├── transformer.py
│   │   │   └── loader.py
│   │   └── topography/
│   │       ├── __init__.py
│   │       ├── extractor.py
│   │       └── loader.py
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── trajectory.py
│   │   ├── atmosphere.py
│   │   └── forces.py
│   ├── optimizer/
│   │   ├── __init__.py
│   │   └── gemini_optimizer.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_physics.py
│   └── test_etl.py
├── docker-compose.yml
├── Dockerfile.airflow
├── Dockerfile.backend
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 11. Features for Recruiters

### Impressive Technical Points:
1. **Full-stack Data Engineering**: ETL + Orchestration + ML
2. **Physics Simulation**: Real ballistic calculations with air resistance
3. **AI Integration**: Gemini for intelligent parameter optimization
4. **Cloud-native**: Docker Compose, PostgreSQL, Redis
5. **Professional ML Ops**: Airflow DAGs, task scheduling, monitoring
6. **API Design**: RESTful with FastAPI, validation, docs
7. **Code Quality**: Type hints, docstrings, tests
8. **3D Visualization**: React + Chart.js for trajectory plots

### Skills Demonstrated:
- Python (NumPy, SciPy, FastAPI)
- Data Engineering (ETL, Airflow)
- ML/AI (Gemini API integration)
- Physics simulation
- Docker & containerization
- API design
- Software architecture
- Testing
