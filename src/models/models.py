from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.utils.datetime_helper import utc_now


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    created_at = Column(DateTime, default=utc_now)

    # Relationship to metrics
    metrics = relationship("Metric", back_populates="sensor")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    metric_type = Column(String, index=True)  # e.g., 'temperature', 'humidity', 'wind_speed'
    value = Column(Float)
    timestamp = Column(DateTime, default=utc_now, index=True)

    # Relationship to sensor
    sensor = relationship("Sensor", back_populates="metrics")