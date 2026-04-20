import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests
import structlog

logger = structlog.get_logger()

USE_MOCK_DATA = os.getenv("APP_ENV") == "test" or not os.getenv("OPENWEATHERMAP_API_KEY")


@dataclass
class WeatherData:
    lat: float
    lon: float
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    wind_direction: float
    cloud_coverage: Optional[int] = None
    visibility: Optional[float] = None
    timestamp: datetime = None
    is_mock: bool = False


class WeatherExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self._use_mock = USE_MOCK_DATA or not self.api_key or self.api_key.startswith("mock_")

    def extract(self, lat: float, lon: float) -> WeatherData:
        logger.info("extracting_weather_data", lat=lat, lon=lon, mock=self._use_mock)

        if self._use_mock:
            return self._create_mock_data(lat, lon)

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return WeatherData(
                lat=lat,
                lon=lon,
                temperature=data["main"]["temp"],
                pressure=data["main"]["pressure"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                wind_direction=data["wind"].get("deg", 0),
                cloud_coverage=data.get("clouds", {}).get("all"),
                visibility=data.get("visibility"),
                timestamp=datetime.fromtimestamp(data["dt"]),
            )
        except Exception as e:
            logger.warning(f"Failed to fetch weather, using mock: {e}")
            return self._create_mock_data(lat, lon)

    def _create_mock_data(self, lat: float, lon: float) -> WeatherData:
        return WeatherData(
            lat=lat,
            lon=lon,
            temperature=22.5,
            pressure=1013.25,
            humidity=65,
            wind_speed=3.5,
            wind_direction=180,
            cloud_coverage=10,
            visibility=10000,
            timestamp=datetime.now(),
            is_mock=True,
        )

    def extract_batch(self, locations: list[tuple[float, float]]) -> list[WeatherData]:
        results = []
        for lat, lon in locations:
            try:
                data = self.extract(lat, lon)
                results.append(data)
            except Exception as e:
                logger.error("failed_to_extract", lat=lat, lon=lon, error=str(e))
        return results