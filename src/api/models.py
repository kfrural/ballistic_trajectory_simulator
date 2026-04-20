from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TrajectoryRequest(BaseModel):
    v0: float = Field(..., gt=0, le=1000, description="Initial velocity in m/s")
    elevation: float = Field(..., ge=0, le=90, description="Elevation angle in degrees")
    azimuth: float = Field(default=0, ge=0, le=360, description="Azimuth angle in degrees")
    include_drag: bool = Field(default=False, description="Include air resistance")
    include_wind: bool = Field(default=False, description="Include wind effects")
    wind_u: float = Field(default=0, description="Wind U component (m/s)")
    wind_v: float = Field(default=0, description="Wind V component (m/s)")
    dt: float = Field(default=0.01, description="Time step in seconds")


class TrajectoryPoint(BaseModel):
    time: float
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    velocity: float


class TrajectoryResponse(BaseModel):
    points: list[TrajectoryPoint]
    max_range: float
    max_altitude: float
    flight_time: float
    time_of_flight: float
    landing_velocity: Optional[float] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class OptimizationRequest(BaseModel):
    target_distance: float = Field(..., gt=0, description="Target distance in meters")
    target_altitude: float = Field(default=0, description="Target altitude in meters")
    weather_data: Optional[dict] = Field(default=None, description="Weather conditions")
    constraints: Optional[dict] = Field(default=None, description="Optimization constraints")


class OptimizationResponse(BaseModel):
    success: bool
    parameters: Optional[dict] = None
    iterations: int
    final_error: float
    trajectory_data: Optional[dict] = None
    message: str


class WeatherResponse(BaseModel):
    lat: float
    lon: float
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    wind_direction: float
    air_density: float
    timestamp: str


class TopographyResponse(BaseModel):
    lat: float
    lon: float
    elevation: float
    terrain_type: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)