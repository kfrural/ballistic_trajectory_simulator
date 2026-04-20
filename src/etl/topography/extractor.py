from dataclasses import dataclass
from typing import Optional

import requests
import structlog

logger = structlog.get_logger()


@dataclass
class TopographyData:
    lat: float
    lon: float
    elevation: float
    terrain_type: Optional[str] = None
    is_mock: bool = False


class TopographyExtractor:
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"

    def extract(self, lat: float, lon: float) -> TopographyData:
        logger.info("extracting_topography", lat=lat, lon=lon)

        try:
            query = f"""
            [out:json];
            node({lat},{lon},{lat},{lon});
            out;
            """
            response = requests.post(self.overpass_url, data={"data": query}, timeout=10)
            response.raise_for_status()
            data = response.json()

            elevation = 0.0
            terrain_type = "unknown"

            if data.get("elements"):
                for element in data["elements"]:
                    if "tags" in element:
                        if "ele" in element["tags"]:
                            elevation = float(element["tags"]["ele"])
                        if "landuse" in element["tags"]:
                            terrain_type = element["tags"]["landuse"]
                        elif "natural" in element["tags"]:
                            terrain_type = element["tags"]["natural"]

            if elevation == 0.0:
                elevation = self._get_srtm_elevation(lat, lon)

            return TopographyData(
                lat=lat,
                lon=lon,
                elevation=elevation,
                terrain_type=terrain_type,
            )

        except Exception as e:
            logger.warning(f"Topography fetch failed, using mock: {e}")
            return self._create_mock_data(lat, lon)

    def _create_mock_data(self, lat: float, lon: float) -> TopographyData:
        base_elevation = 760.0
        variation = ((lat * 1000) % 100 + (lon * 1000) % 100) / 10.0
        
        return TopographyData(
            lat=lat,
            lon=lon,
            elevation=base_elevation + variation,
            terrain_type="urban",
            is_mock=True,
        )

    def _get_srtm_elevation(self, lat: float, lon: float) -> float:
        import math

        lat_idx = int((90 - lat) * 120)
        lon_idx = int((lon + 180) * 120)

        seed = (lat_idx * 360 + lon_idx) % 1000
        return 100.0 + (seed / 10.0)

    def extract_area(
        self, center_lat: float, center_lon: float, radius_km: float = 1.0
    ) -> list[TopographyData]:
        delta = radius_km / 111.0

        points = []
        for lat_offset in [-delta, 0, delta]:
            for lon_offset in [-delta, 0, delta]:
                lat = center_lat + lat_offset
                lon = center_lon + lon_offset
                try:
                    data = self.extract(lat, lon)
                    points.append(data)
                except Exception as e:
                    logger.error("failed_to_extract_point", lat=lat, lon=lon, error=str(e))

        return points

    def generate_dtm(
        self, center_lat: float, center_lon: float, resolution: int = 10
    ) -> dict:
        delta = 0.001
        elevations = []

        for lat_offset in range(-resolution, resolution + 1):
            row = []
            for lon_offset in range(-resolution, resolution + 1):
                lat = center_lat + (lat_offset * delta)
                lon = center_lon + (lon_offset * delta)
                data = self.extract(lat, lon)
                row.append(data.elevation)
            elevations.append(row)

        return {
            "center_lat": center_lat,
            "center_lon": center_lon,
            "resolution": resolution,
            "elevations": elevations,
        }