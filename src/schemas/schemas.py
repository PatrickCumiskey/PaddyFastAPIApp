from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_validator


class MetricType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind_speed"
    PRESSURE = "pressure"
    RAINFALL = "rainfall"


class StatisticType(str, Enum):
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    AVG = "avg"


class SensorCreate(BaseModel):
    name: str
    location: str


class MetricCreate(BaseModel):
    sensor_id: int
    metric_type: MetricType
    value: float


class SensorResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MetricResponse(BaseModel):
    id: int
    sensor_id: int
    metric_type: str
    value: float
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


class QueryParams(BaseModel):
    sensor_ids: Optional[List[int]] = None
    metric_types: List[MetricType]
    statistic: StatisticType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator('end_date', 'start_date', mode='before')
    @classmethod
    def parse_dates(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, end_date, info):
        values = info.data
        start_date = values.get('start_date')

        # If no dates provided, default to the latest data
        if not start_date and not end_date:
            return None

        if start_date and end_date:
            # Ensure end_date is after start_date
            if end_date < start_date:
                raise ValueError("end_date must be after start_date")

            # Check if date range is between one day and one month
            delta = end_date - start_date
            if delta < timedelta(days=1):
                raise ValueError("Date range must be at least one day")
            if delta > timedelta(days=31):
                raise ValueError("Date range must not exceed one month")

        return end_date


class BaseQueryResult(BaseModel):
    """Base class for query results with common fields."""
    metric_type: str
    statistic: str
    value: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class SingleSensorQueryResult(BaseQueryResult):
    """
    Result for MIN and MAX queries that return a single sensor.
    """
    sensor_id: int


class MultiSensorQueryResult(BaseQueryResult):
    """
    Result for AVG and SUM queries that include multiple sensors.
    """
    sensor_ids: List[int]


# Factory function to create the appropriate result type
def create_query_result(statistic: str, **kwargs):
    """Create the appropriate query result based on the statistic type."""
    # Make sure statistic is included in kwargs
    kwargs['statistic'] = statistic

    # Check if the statistic is min or max (as strings)
    if statistic in ("min", "max"):
        return SingleSensorQueryResult(**kwargs)
    else:
        return MultiSensorQueryResult(**kwargs)