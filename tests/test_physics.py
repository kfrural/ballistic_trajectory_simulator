import math
import pytest
import numpy as np

from src.physics.trajectory import BallisticTrajectory, compute_trajectory_fast
from src.physics.atmosphere import AtmosphereModel, ISA
from src.physics.forces import DragForce, WindForce, CoriolisForce


class TestBallisticTrajectory:
    def test_basic_trajectory_45_degrees(self):
        trajectory = BallisticTrajectory(v0=100, elevation=45)
        result = trajectory.calculate_basic()

        assert result.max_range > 0
        assert result.max_altitude > 0
        assert result.flight_time > 0

        expected_range = (100**2) / 9.80665
        assert abs(result.max_range - expected_range) < 10

    def test_basic_trajectory_vertical(self):
        trajectory = BallisticTrajectory(v0=100, elevation=90)
        result = trajectory.calculate_basic()

        expected_altitude = (100**2) / (2 * 9.80665)
        assert abs(result.max_altitude - expected_altitude) < 10

    def test_trajectory_with_drag(self):
        trajectory = BallisticTrajectory(
            v0=250,
            elevation=45,
            drag_coefficient=0.47,
            mass=10.0,
            cross_sectional_area=0.02,
        )
        result = trajectory.calculate_with_drag()

        assert len(result.points) > 0
        assert result.max_range < 250**2 / 9.80665

    def test_trajectory_with_wind(self):
        trajectory = BallisticTrajectory(v0=200, elevation=45)
        result = trajectory.calculate_with_wind(wind_u=5.0, wind_v=0.0)

        assert len(result.points) > 0

    def test_compute_trajectory_fast(self):
        result = compute_trajectory_fast(v0=100, elevation=45, dt=0.05)

        assert "x" in result
        assert "y" in result
        assert "time" in result
        assert result["max_range"] > 0


class TestAtmosphereModel:
    def test_isa_temperature(self):
        assert ISA.temperature(0) == 288.15
        assert ISA.temperature(10000) < 288.15

    def test_isa_density(self):
        rho = ISA.density(0)
        assert rho > 0

    def test_atmosphere_density_calculation(self):
        model = AtmosphereModel()
        rho = model.calculate_density(0)
        assert abs(rho - 1.225) < 0.1


class TestForces:
    def test_drag_force(self):
        drag = DragForce(air_density=1.225)
        velocity = np.array([100.0, 50.0, 0.0])
        position = np.array([0.0, 0.0, 0.0])

        force = drag.calculate(position, velocity)

        assert len(force) == 3
        assert np.all(force <= 0)

    def test_coriolis_force(self):
        coriolis = CoriolisForce(latitude=45)
        velocity = np.array([100.0, 50.0, 0.0])
        position = np.array([0.0, 0.0, 0.0])

        force = coriolis.calculate(position, velocity)

        assert len(force) == 3

    def test_wind_force(self):
        wind = WindForce(wind_velocity=(10.0, 5.0))
        velocity = np.array([100.0, 50.0, 0.0])
        position = np.array([0.0, 0.0, 0.0])

        force = wind.calculate(position, velocity)

        assert len(force) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])