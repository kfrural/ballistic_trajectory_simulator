import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.physics.trajectory import BallisticTrajectory, compute_trajectory_fast
from src.etl.weather import WeatherExtractor, WeatherTransformer
from src.etl.topography import TopographyExtractor
from src.optimizer import GeminiOptimizer
from .models import (
    TrajectoryResponse,
    TrajectoryPoint,
    OptimizationResponse,
    WeatherResponse,
    TopographyResponse,
    HealthResponse,
)

router = APIRouter()


@router.post("/simulate", response_model=TrajectoryResponse)
async def simulate_trajectory(request: dict) -> TrajectoryResponse:
    v0 = request.get("v0", 250)
    elevation = request.get("elevation", 45)
    azimuth = request.get("azimuth", 0)
    include_drag = request.get("include_drag", False)
    include_wind = request.get("include_wind", False)
    wind_u = request.get("wind_u", 0)
    wind_v = request.get("wind_v", 0)
    dt = request.get("dt", 0.01)

    trajectory = BallisticTrajectory(
        v0=v0,
        elevation=elevation,
        azimuth=azimuth,
    )

    if include_wind:
        result = trajectory.calculate_with_wind(wind_u, wind_v, dt)
    elif include_drag:
        result = trajectory.calculate_with_drag(dt)
    else:
        result = trajectory.calculate_basic(dt)

    return TrajectoryResponse(
        points=[
            TrajectoryPoint(
                time=p.time,
                x=p.x,
                y=p.y,
                z=p.z,
                vx=p.vx,
                vy=p.vy,
                vz=p.vz,
                velocity=p.velocity,
            )
            for p in result.points
        ],
        max_range=result.max_range,
        max_altitude=result.max_altitude,
        flight_time=result.flight_time,
        time_of_flight=result.time_of_flight,
        landing_velocity=result.landing_velocity,
    )


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_parameters(request: dict) -> OptimizationResponse:
    target_distance = request.get("target_distance", 3000)
    target_altitude = request.get("target_altitude", 0)
    weather_data = request.get("weather_data")
    constraints = request.get("constraints")

    constraints = constraints or {
        "max_elevation": 85,
        "min_elevation": 5,
        "max_velocity": 400,
        "min_velocity": 50,
    }

    optimizer = GeminiOptimizer()

    result = optimizer.optimize(
        target_distance=target_distance,
        target_altitude=target_altitude,
        weather_data=weather_data,
        constraints=constraints,
    )

    return OptimizationResponse(
        success=result.success,
        parameters={
            "elevation_angle": result.parameters.elevation_angle,
            "azimuth_angle": result.parameters.azimuth_angle,
            "charge_level": result.parameters.charge_level,
            "estimated_range": result.parameters.estimated_range,
            "estimated_flight_time": result.parameters.estimated_flight_time,
        }
        if result.parameters
        else None,
        iterations=result.iterations,
        final_error=result.final_error,
        trajectory_data=result.trajectory_data,
        message=result.message,
    )


@router.get("/weather/{lat}/{lon}", response_model=WeatherResponse)
async def get_weather(lat: float, lon: float) -> WeatherResponse:
    try:
        extractor = WeatherExtractor()
        raw_data = extractor.extract(lat, lon)

        transformer = WeatherTransformer()
        transformed = transformer.transform(raw_data)

        return WeatherResponse(
            lat=transformed.lat,
            lon=transformed.lon,
            temperature=transformed.temperature,
            pressure=transformed.pressure,
            humidity=transformed.humidity,
            wind_speed=transformed.wind_speed,
            wind_direction=transformed.wind_direction,
            air_density=transformed.air_density,
            timestamp=transformed.timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather fetch failed: {str(e)}")


@router.get("/terrain/{lat}/{lon}", response_model=TopographyResponse)
async def get_terrain(lat: float, lon: float) -> TopographyResponse:
    try:
        extractor = TopographyExtractor()
        data = extractor.extract(lat, lon)

        return TopographyResponse(
            lat=data.lat,
            lon=data.lon,
            elevation=data.elevation,
            terrain_type=data.terrain_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terrain fetch failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )