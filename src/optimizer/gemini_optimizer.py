import json
import math
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

import structlog

from src.physics.trajectory import BallisticTrajectory

logger = structlog.get_logger()


@dataclass
class FireParameters:
    elevation_angle: float
    azimuth_angle: float
    charge_level: float
    estimated_range: float
    estimated_flight_time: float


@dataclass
class OptimizationResult:
    success: bool
    parameters: Optional[FireParameters]
    iterations: int
    final_error: float
    trajectory_data: Optional[dict]
    message: str


class GeminiOptimizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = None
        self._use_mock = not self.api_key or self.api_key.startswith("mock_")
        
        if self._use_mock:
            logger.info("Using local optimization (mock mode)")
        elif self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini, using local: {e}")
                self._use_mock = True

    def optimize(
        self,
        target_distance: float,
        target_altitude: float = 0.0,
        initial_position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        weather_data: Optional[dict] = None,
        constraints: Optional[dict] = None,
    ) -> OptimizationResult:
        logger.info(
            "starting_optimization",
            target_distance=target_distance,
            target_altitude=target_altitude,
        )

        constraints = constraints or {
            "max_elevation": 85.0,
            "min_elevation": 5.0,
            "max_velocity": 400.0,
            "min_velocity": 50.0,
        }

        if self.model and self.api_key:
            return self._optimize_with_gemini(
                target_distance,
                target_altitude,
                initial_position,
                weather_data,
                constraints,
            )
        else:
            return self._optimize_locally(
                target_distance,
                target_altitude,
                weather_data,
                constraints,
            )

    def _optimize_with_gemini(
        self,
        target_distance: float,
        target_altitude: float,
        initial_position: tuple,
        weather_data: Optional[dict],
        constraints: dict,
    ) -> OptimizationResult:
        prompt = self._build_optimization_prompt(
            target_distance,
            target_altitude,
            weather_data,
            constraints,
        )

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            try:
                result = json.loads(response_text)
                return self._parse_gemini_result(result, target_distance, weather_data)
            except json.JSONDecodeError:
                return self._optimize_locally(
                    target_distance, target_altitude, weather_data, constraints
                )

        except Exception as e:
            logger.error("gemini_optimization_failed", error=str(e))
            return self._optimize_locally(
                target_distance, target_altitude, weather_data, constraints
            )

    def _build_optimization_prompt(
        self,
        target_distance: float,
        target_altitude: float,
        weather_data: Optional[dict],
        constraints: dict,
    ) -> str:
        weather_str = ""
        if weather_data:
            weather_str = f"""
Weather conditions:
- Wind speed: {weather_data.get('wind_speed', 0)} m/s
- Wind direction: {weather_data.get('wind_direction', 0)} degrees
- Temperature: {weather_data.get('temperature', 15)} °C
- Pressure: {weather_data.get('pressure', 1013)} hPa
- Air density: {weather_data.get('air_density', 1.225)} kg/m³
"""

        prompt = f"""You are an expert ballistic calculator. Find the optimal firing parameters to hit a target.

Target specifications:
- Distance: {target_distance} meters
- Altitude: {target_altitude} meters

Constraints:
- Max elevation: {constraints['max_elevation']} degrees
- Min elevation: {constraints['min_elevation']} degrees
- Max velocity: {constraints['max_velocity']} m/s

{weather_str}

Find the optimal:
- Elevation angle (degrees)
- Initial velocity (m/s)
- Estimated flight time

Respond with a JSON object:
{{
  "elevation_angle": <degrees>,
  "initial_velocity": <m/s>,
  "estimated_flight_time": <seconds>,
  "estimated_range": <meters>
}}
"""
        return prompt

    def _parse_gemini_result(
        self, result: dict, target_distance: float, weather_data: Optional[dict]
    ) -> OptimizationResult:
        elevation = result.get("elevation_angle", 45)
        velocity = result.get("initial_velocity", 200)

        params = FireParameters(
            elevation_angle=elevation,
            azimuth_angle=0.0,
            charge_level=1.0,
            estimated_range=result.get("estimated_range", target_distance),
            estimated_flight_time=result.get("estimated_flight_time", 10.0),
        )

        trajectory = BallisticTrajectory(v0=velocity, elevation=elevation)
        trajectory_result = trajectory.calculate_basic()

        final_error = abs(trajectory_result.max_range - target_distance)

        return OptimizationResult(
            success=True,
            parameters=params,
            iterations=1,
            final_error=final_error,
            trajectory_data={
                "x": [p.x for p in trajectory_result.points],
                "y": [p.y for p in trajectory_result.points],
                "time": [p.time for p in trajectory_result.points],
            },
            message="Optimization completed using Gemini AI",
        )

    def _optimize_locally(
        self,
        target_distance: float,
        target_altitude: float,
        weather_data: Optional[dict],
        constraints: dict,
    ) -> OptimizationResult:
        logger.info("running_local_optimization")

        wind_u = weather_data.get("wind_u", 0) if weather_data else 0
        wind_v = weather_data.get("wind_v", 0) if weather_data else 0

        best_params = None
        best_error = float("inf")

        elevation_range = range(int(constraints["min_elevation"]), int(constraints["max_elevation"]) + 1, 1)
        velocity_range = range(50, int(constraints["max_velocity"]) + 1, 10)

        for elevation in elevation_range:
            for velocity in velocity_range:
                trajectory = BallisticTrajectory(
                    v0=velocity,
                    elevation=elevation,
                )

                if weather_data:
                    result = trajectory.calculate_with_wind(wind_u, wind_v)
                else:
                    result = trajectory.calculate_basic()

                error = abs(result.max_range - target_distance)

                if error < best_error:
                    best_error = error
                    best_params = FireParameters(
                        elevation_angle=elevation,
                        azimuth_angle=0.0,
                        charge_level=velocity / constraints["max_velocity"],
                        estimated_range=result.max_range,
                        estimated_flight_time=result.flight_time,
                    )

        trajectory = BallisticTrajectory(
            v0=constraints["max_velocity"] * (best_params.charge_level if best_params else 0.5),
            elevation=best_params.elevation_angle if best_params else 45,
        )

        if best_params and weather_data:
            result = trajectory.calculate_with_wind(wind_u, wind_v)
        else:
            result = trajectory.calculate_basic()

        return OptimizationResult(
            success=best_error < 500,
            parameters=best_params,
            iterations=len(list(elevation_range)) * len(list(velocity_range)),
            final_error=best_error,
            trajectory_data={
                "x": [p.x for p in result.points],
                "y": [p.y for p in result.points],
                "time": [p.time for p in result.points],
            },
            message=f"Local optimization completed with error: {best_error:.2f}m",
        )

    def optimize_batch(
        self,
        targets: list[dict],
        weather_data: Optional[dict] = None,
    ) -> list[OptimizationResult]:
        results = []
        for target in targets:
            result = self.optimize(
                target_distance=target["distance"],
                target_altitude=target.get("altitude", 0),
                weather_data=weather_data,
            )
            results.append(result)
        return results