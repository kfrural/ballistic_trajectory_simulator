import json
import os
from typing import Optional

import redis
import structlog
from sqlalchemy import create_engine, Column, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert

logger = structlog.get_logger()

Base = declarative_base()


class TopographyRecord(Base):
    __tablename__ = "topography_data"

    id = Column(Float, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    terrain_type = Column(String(50))
    timestamp = Column(DateTime)


class TopographyLoader:
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        redis_url: Optional[str] = None,
    ):
        self.db_connection_string = db_connection_string or os.getenv(
            "DATABASE_URL", "postgresql://localhost/ballistic_sim"
        )
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.engine = create_engine(self.db_connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.redis_client = None

    def _get_redis(self):
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        return self.redis_client

    def load(self, topography_data: list) -> None:
        logger.info("loading_topography_data", count=len(topography_data))

        session = self.Session()
        try:
            for data in topography_data:
                record = TopographyRecord(
                    lat=data.lat,
                    lon=data.lon,
                    elevation=data.elevation,
                    terrain_type=data.terrain_type,
                )
                session.add(record)
            session.commit()
            logger.info("topography_loaded_successfully", count=len(topography_data))
        except Exception as e:
            session.rollback()
            logger.error("failed_to_load_topography", error=str(e))
            raise
        finally:
            session.close()

    def cache_dtm(self, dtm_data: dict) -> None:
        redis_client = self._get_redis()
        key = f"dtm:{dtm_data['center_lat']}:{dtm_data['center_lon']}"
        redis_client.setex(key, 3600, json.dumps(dtm_data))
        logger.info("dtm_cached", key=key)

    def get_cached_dtm(self, lat: float, lon: float) -> Optional[dict]:
        redis_client = self._get_redis()
        key = f"dtm:{lat}:{lon}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        cached_dtm = self.get_cached_dtm(lat, lon)
        if cached_dtm:
            center_idx = cached_dtm["resolution"]
            return cached_dtm["elevations"][center_idx][center_idx]

        session = self.Session()
        try:
            record = (
                session.query(TopographyRecord)
                .filter(
                    TopographyRecord.lat == lat,
                    TopographyRecord.lon == lon,
                )
                .first()
            )
            return record.elevation if record else None
        finally:
            session.close()