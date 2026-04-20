import math
from dataclasses import dataclass
from typing import Protocol

import numpy as np


class Force(Protocol):
    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        ...


@dataclass
class DragCoefficient:
    sphere: float = 0.47
    hemisphere: float = 0.42
    ogive: float = 0.38
    spitzer: float = 0.29
    apollo_capusle: float = 0.50


@dataclass
class ProjectileProperties:
    mass: float
    cross_sectional_area: float
    drag_coefficient: float = 0.47
    length: float = 0.0


class DragForce:
    def __init__(self, air_density: float = 1.225, projectile: ProjectileProperties = None):
        self.air_density = air_density
        self.projectile = projectile or ProjectileProperties(
            mass=1.0, cross_sectional_area=0.01, drag_coefficient=0.47
        )
        self.Cd = self.projectile.drag_coefficient

    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        v = np.linalg.norm(velocity)
        if v < 1e-6:
            return np.zeros(3)

        F_drag = -0.5 * self.air_density * self.Cd * self.projectile.cross_sectional_area * v * velocity

        return F_drag / self.projectile.mass

    def calculate_scalar(self, velocity: float) -> float:
        return 0.5 * self.air_density * self.Cd * self.projectile.cross_sectional_area * velocity**2


class WindForce:
    def __init__(self, wind_velocity: tuple[float, float] = (0.0, 0.0)):
        self.wind_u = wind_velocity[0]
        self.wind_v = wind_velocity[1]

    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        relative_velocity = np.array(
            [velocity[0] - self.wind_u, velocity[1] - self.wind_v, velocity[2]]
        )

        relative_v = np.linalg.norm(relative_velocity)
        if relative_v < 1e-6:
            return np.zeros(3)

        drag_force = -0.5 * 1.225 * 0.47 * 0.01 * relative_v * relative_velocity

        return drag_force


class CoriolisForce:
    def __init__(self, latitude: float = 0.0, earth_rotation_rate: float = 7.2921e-5):
        self.latitude = latitude
        self.Omega = earth_rotation_rate
        self.coriolis_parameter = 2 * self.Omega * math.sin(math.radians(latitude))

    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        v = velocity
        f = self.coriolis_parameter

        coriolis = np.array([-f * v[1], f * v[0], 0])

        return coriolis


class GravityForce:
    def __init__(self, g: float = 9.80665):
        self.g = g

    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        return np.array([0, -self.g, 0])


class MagnusForce:
    def __init__(self, spin_rate: float = 1000.0):
        self.spin_rate = spin_rate

    def calculate(self, position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        v = np.linalg.norm(velocity)
        if v < 1e-6:
            return np.zeros(3)

        v_normalized = velocity / v

        spin_magnitude = self.spin_rate * 0.001

        magnus = spin_magnitude * np.cross(v_normalized, np.array([0, 0, 1]))

        return magnus


def compute_forces_comprehensive(
    position: np.ndarray,
    velocity: np.ndarray,
    mass: float = 1.0,
    area: float = 0.01,
    Cd: float = 0.47,
    air_density: float = 1.225,
    wind: tuple[float, float] = (0.0, 0.0),
    latitude: float = 0.0,
    spin: float = 0.0,
) -> np.ndarray:
    gravity = GravityForce()
    drag = DragForce(air_density, ProjectileProperties(mass, area, Cd))

    rel_vel = np.array(
        [velocity[0] - wind[0], velocity[1] - wind[1], velocity[2]]
    )

    F_gravity = gravity.calculate(position, velocity)
    F_drag = drag.calculate(position, rel_vel)

    total_force = F_gravity + F_drag

    if latitude != 0.0:
        coriolis = CoriolisForce(latitude)
        total_force += coriolis.calculate(position, velocity)

    if spin != 0.0:
        magnus = MagnusForce(spin)
        total_force += magnus.calculate(position, velocity)

    return total_force