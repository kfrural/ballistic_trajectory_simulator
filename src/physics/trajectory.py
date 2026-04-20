import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import structlog

logger = structlog.get_logger()

GRAVITY = 9.80665


@dataclass
class TrajectoryPoint:
    time: float
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    velocity: float


@dataclass
class TrajectoryResult:
    points: list[TrajectoryPoint]
    max_range: float
    max_altitude: float
    flight_time: float
    time_of_flight: float
    landing_velocity: Optional[float] = None


class BallisticTrajectory:
    def __init__(
        self,
        v0: float,
        elevation: float,
        azimuth: float = 0.0,
        drag_coefficient: float = 0.47,
        mass: float = 1.0,
        cross_sectional_area: float = 0.01,
    ):
        self.v0 = v0
        self.elevation = math.radians(elevation)
        self.azimuth = math.radians(azimuth)
        self.drag_coefficient = drag_coefficient
        self.mass = mass
        self.cross_sectional_area = cross_sectional_area
        self.air_density = 1.225

    def calculate_basic(self, dt: float = 0.01) -> TrajectoryResult:
        logger.info(
            "calculating_basic_trajectory",
            v0=self.v0,
            elevation_deg=math.degrees(self.elevation),
        )

        v0x = self.v0 * math.cos(self.elevation)
        v0y = self.v0 * math.sin(self.elevation)

        g = GRAVITY
        points = []

        t = 0.0
        x, y = 0.0, 0.0

        while y >= 0 or t == 0:
            x = v0x * t
            y = v0y * t - 0.5 * g * t**2

            if y < 0 and t > 0:
                t_flight = 2 * v0y / g
                x = v0x * t_flight
                y = 0
                break

            vx = v0x
            vy = v0y - g * t
            velocity = math.sqrt(vx**2 + vy**2)

            points.append(
                TrajectoryPoint(
                    time=round(t, 3),
                    x=round(x, 2),
                    y=round(y, 2),
                    z=0.0,
                    vx=round(vx, 2),
                    vy=round(vy, 2),
                    vz=0.0,
                    velocity=round(velocity, 2),
                )
            )

            t += dt

        max_altitude = (v0y**2) / (2 * g)
        time_of_flight = 2 * v0y / g

        return TrajectoryResult(
            points=points,
            max_range=round(x, 2),
            max_altitude=round(max_altitude, 2),
            flight_time=round(t, 2),
            time_of_flight=round(time_of_flight, 2),
        )

    def calculate_with_drag(self, dt: float = 0.01, method: str = "rk4") -> TrajectoryResult:
        logger.info(
            "calculating_trajectory_with_drag",
            v0=self.v0,
            method=method,
        )

        k = (self.drag_coefficient * self.air_density * self.cross_sectional_area) / (2 * self.mass)

        v0x = self.v0 * math.cos(self.elevation)
        v0y = self.v0 * math.sin(self.elevation)

        state = np.array([0.0, 0.0, v0x, v0y])

        points = []
        t = 0.0

        while True:
            if method == "euler":
                state = self._euler_step(state, k, dt)
            else:
                state = self._rk4_step(state, k, dt)

            x, y, vx, vy = state

            if y < 0:
                break

            velocity = math.sqrt(vx**2 + vy**2)

            points.append(
                TrajectoryPoint(
                    time=round(t, 3),
                    x=round(x, 2),
                    y=round(y, 2),
                    z=0.0,
                    vx=round(vx, 2),
                    vy=round(vy, 2),
                    vz=0.0,
                    velocity=round(velocity, 2),
                )
            )

            t += dt

        max_range = state[0]
        max_altitude = max(p.y for p in points) if points else 0

        return TrajectoryResult(
            points=points,
            max_range=round(max_range, 2),
            max_altitude=round(max_altitude, 2),
            flight_time=round(t, 2),
            time_of_flight=round(t, 2),
            landing_velocity=round(math.sqrt(state[2]**2 + state[3]**2), 2),
        )

    def _acceleration(self, state: np.ndarray, k: float) -> np.ndarray:
        x, y, vx, vy = state
        v = math.sqrt(vx**2 + vy**2)

        ax = -k * v * vx
        ay = -GRAVITY - k * v * vy

        return np.array([vx, vy, ax, ay])

    def _euler_step(self, state: np.ndarray, k: float, dt: float) -> np.ndarray:
        acc = self._acceleration(state, k)
        new_state = state + acc * dt

        mid_x = state[0] + state[2] * dt / 2
        mid_y = state[1] + state[3] * dt / 2
        mid_vx = state[2] + acc[2] * dt / 2
        mid_vy = state[3] + acc[3] * dt / 2

        mid_state = np.array([mid_x, mid_y, mid_vx, mid_vy])
        acc_mid = self._acceleration(mid_state, k)

        return state + acc_mid * dt

    def _rk4_step(self, state: np.ndarray, k: float, dt: float) -> np.ndarray:
        k1 = self._acceleration(state, k)
        k2 = self._acceleration(state + k1 * dt / 2, k)
        k3 = self._acceleration(state + k2 * dt / 2, k)
        k4 = self._acceleration(state + k3 * dt, k)

        return state + (k1 + 2*k2 + 2*k3 + k4) * dt / 6

    def calculate_with_wind(
        self,
        wind_u: float = 0.0,
        wind_v: float = 0.0,
        dt: float = 0.01,
    ) -> TrajectoryResult:
        logger.info("calculating_trajectory_with_wind", wind_u=wind_u, wind_v=wind_v)

        k = (self.drag_coefficient * self.air_density * self.cross_sectional_area) / (2 * self.mass)

        v0x = self.v0 * math.cos(self.elevation)
        v0y = self.v0 * math.sin(self.elevation)

        state = np.array([0.0, 0.0, v0x - wind_u, v0y - wind_v])

        points = []
        t = 0.0

        while True:
            state = self._rk4_step_wind(state, k, wind_u, wind_v, dt)

            x, y, vx, vy = state

            if y < 0:
                break

            velocity = math.sqrt((vx + wind_u)**2 + (vy + wind_v)**2)

            points.append(
                TrajectoryPoint(
                    time=round(t, 3),
                    x=round(x, 2),
                    y=round(y, 2),
                    z=0.0,
                    vx=round(vx + wind_u, 2),
                    vy=round(vy + wind_v, 2),
                    vz=0.0,
                    velocity=round(velocity, 2),
                )
            )

            t += dt

        max_range = state[0]
        max_altitude = max(p.y for p in points) if points else 0

        return TrajectoryResult(
            points=points,
            max_range=round(max_range, 2),
            max_altitude=round(max_altitude, 2),
            flight_time=round(t, 2),
            time_of_flight=round(t, 2),
            landing_velocity=round(math.sqrt(state[2]**2 + state[3]**2), 2),
        )

    def _rk4_step_wind(
        self, state: np.ndarray, k: float, wind_u: float, wind_v: float, dt: float
    ) -> np.ndarray:
        x, y, vx, vy = state
        rel_vx = vx + wind_u
        rel_vy = vy + wind_v
        rel_v = math.sqrt(rel_vx**2 + rel_vy**2)

        v = math.sqrt(vx**2 + vy**2)

        ax = -k * v * rel_vx
        ay = -GRAVITY - k * v * rel_vy

        k1 = np.array([vx, vy, ax, ay])

        state2 = state + k1 * dt / 2
        k2 = self._calc_wind_acc(state2, k, wind_u, wind_v)

        state3 = state + k2 * dt / 2
        k3 = self._calc_wind_acc(state3, k, wind_u, wind_v)

        state4 = state + k3 * dt
        k4 = self._calc_wind_acc(state4, k, wind_u, wind_v)

        return state + (k1 + 2*k2 + 2*k3 + k4) * dt / 6

    def _calc_wind_acc(self, state: np.ndarray, k: float, wind_u: float, wind_v: float):
        x, y, vx, vy = state
        rel_vx = vx + wind_u
        rel_vy = vy + wind_v
        rel_v = math.sqrt(rel_vx**2 + rel_vy**2)

        v = math.sqrt(vx**2 + vy**2)
        if v == 0:
            v = 0.001

        ax = -k * v * rel_vx
        ay = -GRAVITY - k * v * rel_vy

        return np.array([vx, vy, ax, ay])


def compute_trajectory_fast(
    v0: float,
    elevation: float,
    azimuth: float = 0.0,
    max_time: float = 60.0,
    dt: float = 0.05,
) -> dict:
    angle_rad = math.radians(elevation)

    vx0 = v0 * math.cos(angle_rad)
    vy0 = v0 * math.sin(angle_rad)

    times = np.arange(0, max_time, dt)

    x = vx0 * times
    y = vy0 * times - 0.5 * GRAVITY * times**2

    y = np.maximum(y, 0)

    valid_indices = np.where(y >= 0)[0]
    if len(valid_indices) > 0:
        last_idx = valid_indices[-1]
        x = x[: last_idx + 1]
        y = y[: last_idx + 1]
        times = times[: last_idx + 1]

    return {
        "time": times.tolist(),
        "x": x.tolist(),
        "y": y.tolist(),
        "max_range": float(x[-1]),
        "max_altitude": float(np.max(y)),
        "flight_time": float(times[-1]),
    }