import math
from dataclasses import dataclass

import numpy as np


@dataclass
class AtmosphereConditions:
    temperature: float
    pressure: float
    humidity: float
    air_density: float
    speed_of_sound: float


class AtmosphereModel:
    def __init__(
        self,
        reference_density: float = 1.225,
        reference_pressure: float = 101325.0,
        reference_temp: float = 288.15,
    ):
        self.rho0 = reference_density
        self.p0 = reference_pressure
        self.T0 = reference_temp
        self.R = 287.05
        self.gamma = 1.4

    def calculate_density(self, altitude: float, temperature: float = None) -> float:
        if temperature is None:
            temperature = self._get_temperature(altitude)

        return self.rho0 * (temperature / self.T0) ** 4.256

    def _get_temperature(self, altitude: float) -> float:
        if altitude < 11000:
            return self.T0 - 0.0065 * altitude
        elif altitude < 20000:
            return 216.65
        elif altitude < 32000:
            return 216.65 + 0.001 * (altitude - 20000)
        return 228.65 + 0.0028 * (altitude - 32000)

    def calculate_pressure(self, altitude: float) -> float:
        if altitude < 11000:
            return self.p0 * (1 - 0.0000225577 * altitude) ** 5.2559
        elif altitude < 20000:
            return 22632 * math.exp(-(altitude - 11000) / 7000)
        elif altitude < 32000:
            return 5474 * math.exp(-(altitude - 20000) / 6000)
        return 868 * math.exp(-(altitude - 32000) / 4000)

    def calculate_speed_of_sound(self, temperature: float) -> float:
        return math.sqrt(self.gamma * self.R * temperature)

    def get_conditions_at_altitude(self, altitude: float) -> AtmosphereConditions:
        temperature = self._get_temperature(altitude)
        pressure = self.calculate_pressure(altitude)
        air_density = self.calculate_density(altitude, temperature)
        speed_of_sound = self.calculate_speed_of_sound(temperature)

        return AtmosphereConditions(
            temperature=temperature,
            pressure=pressure,
            humidity=0.0,
            air_density=air_density,
            speed_of_sound=speed_of_sound,
        )

    def correct_for_weather(
        self,
        base_density: float,
        temperature: float,
        pressure: float,
        humidity: float,
    ) -> float:
        temp_kelvin = temperature + 273.15

        saturation_vp = 6.1078 * 10 ** (7.5 * temperature / (237.3 + temperature))
        actual_vp = (humidity / 100) * saturation_vp

        partial_pressure = pressure - actual_vp

        rho_dry = (partial_pressure / (self.R * temp_kelvin))
        rho_wet = (actual_vp / (461.5 * temp_kelvin))

        return (rho_dry + rho_wet) * base_density / self.rho0


class ISA:
    @staticmethod
    def temperature(altitude_m: float) -> float:
        if altitude_m < 11000:
            return 288.15 - 0.0065 * altitude_m
        elif altitude_m < 20000:
            return 216.65
        elif altitude_m < 32000:
            return 216.65 + 0.001 * (altitude_m - 20000)
        return 228.65 + 0.0028 * (altitude_m - 32000)

    @staticmethod
    def pressure(altitude_m: float) -> float:
        if altitude_m < 11000:
            return 101325 * (1 - 0.0000225577 * altitude_m) ** 5.2559
        return 101325 * math.exp(-altitude_m / 7000)

    @staticmethod
    def density(altitude_m: float) -> float:
        T = ISA.temperature(altitude_m)
        p = ISA.pressure(altitude_m)
        return p / (287.05 * T)