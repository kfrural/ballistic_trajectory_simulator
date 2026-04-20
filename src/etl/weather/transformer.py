from dataclasses import dataclass
from typing import Optional

import structlog

logger = structlog.get_logger()


@dataclass
class TransformedWeather:
    lat: float
    lon: float
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    wind_direction: float
    air_density: float
    wind_components: tuple[float, float]
    timestamp: str


class WeatherTransformer:
    def __init__(self, reference_pressure: float = 1013.25, reference_temp: float = 15.0):
        self.reference_pressure = reference_pressure
        self.reference_temp = reference_temp
        self.gas_constant = 287.05
        self.molecular_weight_air = 0.028964

    def transform(self, raw_data) -> TransformedWeather:
        logger.info("transforming_weather_data", lat=raw_data.lat, lon=raw_data.lon)

        air_density = self._calculate_air_density(
            raw_data.temperature,
            raw_data.pressure,
            raw_data.humidity,
        )

        wind_u, wind_v = self._calculate_wind_components(
            raw_data.wind_speed,
            raw_data.wind_direction,
        )

        return TransformedWeather(
            lat=raw_data.lat,
            lon=raw_data.lon,
            temperature=raw_data.temperature,
            pressure=raw_data.pressure,
            humidity=raw_data.humidity,
            air_density=air_density,
            wind_speed=raw_data.wind_speed,
            wind_direction=raw_data.wind_direction,
            wind_components=(wind_u, wind_v),
            timestamp=raw_data.timestamp.isoformat(),
        )

    def _calculate_air_density(
        self,
        temperature: float,
        pressure: float,
        humidity: float,
    ) -> float:
        temp_kelvin = temperature + 273.15
        saturation_vapor_pressure = 6.1078 * 10 ** (7.5 * temperature / (237.3 + temperature))
        actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
        partial_pressure = pressure - actual_vapor_pressure
        air_density = (partial_pressure / (self.gas_constant * temp_kelvin)) + (
            actual_vapor_pressure / (461.5 * temp_kelvin)
        )
        return round(air_density, 4)

    def _calculate_wind_components(
        self,
        speed: float,
        direction: float,
    ) -> tuple[float, float]:
        import math
        direction_rad = math.radians(direction)
        wind_u = -speed * math.sin(direction_rad)
        wind_v = -speed * math.cos(direction_rad)
        return round(wind_u, 2), round(wind_v, 2)

    def transform_batch(self, raw_data_list: list) -> list[TransformedWeather]:
        return [self.transform(data) for data in raw_data_list]