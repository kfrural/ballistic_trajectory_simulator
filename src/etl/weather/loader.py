import os
from datetime import datetime
from typing import Optional

import structlog
from sqlalchemy import create_engine, Column, Float, DateTime, String
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import declarative_base, sessionmaker

logger = structlog.get_logger()

Base = declarative_base()


class WeatherRecord(Base):
    __tablename__ = "weather_data"

    id = Column(Float, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Float, nullable=False)
    air_density = Column(Float, nullable=False)
    wind_u = Column(Float, nullable=False)
    wind_v = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class WeatherLoader:
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL", "postgresql://localhost/ballistic_sim"
        )
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def load(self, transformed_data: list) -> None:
        logger.info("loading_weather_data", count=len(transformed_data))

        session = self.Session()
        try:
            for data in transformed_data:
                record = WeatherRecord(
                    lat=data.lat,
                    lon=data.lon,
                    temperature=data.temperature,
                    pressure=data.pressure,
                    humidity=data.humidity,
                    wind_speed=data.wind_speed,
                    wind_direction=data.wind_direction,
                    air_density=data.air_density,
                    wind_u=data.wind_components[0],
                    wind_v=data.wind_components[1],
                    timestamp=datetime.fromisoformat(data.timestamp),
                )
                session.add(record)
            session.commit()
            logger.info("weather_data_loaded_successfully", count=len(transformed_data))
        except Exception as e:
            session.rollback()
            logger.error("failed_to_load_weather_data", error=str(e))
            raise
        finally:
            session.close()

    def get_latest(self, lat: float, lon: float) -> Optional[WeatherRecord]:
        session = self.Session()
        try:
            return (
                session.query(WeatherRecord)
                .filter(
                    WeatherRecord.lat == lat,
                    WeatherRecord.lon == lon,
                )
                .order_by(WeatherRecord.timestamp.desc())
                .first()
            )
        finally:
            session.close()