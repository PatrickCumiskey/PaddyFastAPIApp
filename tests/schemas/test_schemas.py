from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from src.schemas.schemas import (
    SensorCreate, MetricCreate, QueryParams, MetricType, StatisticType
)


def test_sensor_create_schema():
    """Test SensorCreate schema validation"""
    # Valid data
    data = {"name": "Test Sensor", "location": "Test Location"}
    sensor = SensorCreate(**data)
    assert sensor.name == "Test Sensor"
    assert sensor.location == "Test Location"

    # Missing required field
    with pytest.raises(ValidationError):
        SensorCreate(name="Test Sensor")

    with pytest.raises(ValidationError):
        SensorCreate(location="Test Location")


def test_metric_create_schema():
    """Test MetricCreate schema validation"""
    # Valid data
    data = {"sensor_id": 1, "metric_type": "temperature", "value": 25.5}
    metric = MetricCreate(**data)
    assert metric.sensor_id == 1
    assert metric.metric_type == MetricType.TEMPERATURE
    assert metric.value == 25.5

    # Missing required field
    with pytest.raises(ValidationError):
        MetricCreate(sensor_id=1, metric_type="temperature")

    with pytest.raises(ValidationError):
        MetricCreate(sensor_id=1, value=25.5)

    with pytest.raises(ValidationError):
        MetricCreate(metric_type="temperature", value=25.5)

    # Invalid metric type
    with pytest.raises(ValidationError):
        MetricCreate(sensor_id=1, metric_type="invalid", value=25.5)


def test_query_params_schema():
    """Test QueryParams schema validation"""
    # Valid data with all fields
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    data = {
        "sensor_ids": [1, 2, 3],
        "metric_types": ["temperature", "humidity"],
        "statistic": "avg",
        "start_date": week_ago,
        "end_date": now
    }

    query = QueryParams(**data)
    assert query.sensor_ids == [1, 2, 3]
    assert len(query.metric_types) == 2
    assert MetricType.TEMPERATURE in query.metric_types
    assert MetricType.HUMIDITY in query.metric_types
    assert query.statistic == StatisticType.AVG
    assert query.start_date == week_ago
    assert query.end_date == now

    # Valid data with minimal fields
    data = {
        "metric_types": ["temperature"],
        "statistic": "min"
    }

    query = QueryParams(**data)
    assert query.sensor_ids is None
    assert len(query.metric_types) == 1
    assert MetricType.TEMPERATURE in query.metric_types
    assert query.statistic == StatisticType.MIN
    assert query.start_date is None
    assert query.end_date is None

    # Missing required fields
    with pytest.raises(ValidationError):
        QueryParams(sensor_ids=[1], statistic="avg")

    with pytest.raises(ValidationError):
        QueryParams(metric_types=["temperature"])

    # Invalid statistic
    with pytest.raises(ValidationError):
        QueryParams(metric_types=["temperature"], statistic="invalid")

    # Invalid metric type
    with pytest.raises(ValidationError):
        QueryParams(metric_types=["invalid"], statistic="avg")


def test_date_validation():
    """Test date validation in QueryParams"""
    now = datetime.now(timezone.utc)

    # Test date conversion from string
    data = {
        "metric_types": ["temperature"],
        "statistic": "avg",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=1)).isoformat()
    }

    query = QueryParams(**data)
    assert isinstance(query.start_date, datetime)
    assert isinstance(query.end_date, datetime)

    # Test date range validation - end before start
    with pytest.raises(ValidationError):
        QueryParams(
            metric_types=["temperature"],
            statistic="avg",
            start_date=now,
            end_date=now - timedelta(days=1)
        )

    # Test date range validation - less than a day
    with pytest.raises(ValidationError):
        QueryParams(
            metric_types=["temperature"],
            statistic="avg",
            start_date=now,
            end_date=now + timedelta(hours=23)
        )

    # Test date range validation - more than a month
    with pytest.raises(ValidationError):
        QueryParams(
            metric_types=["temperature"],
            statistic="avg",
            start_date=now,
            end_date=now + timedelta(days=32)
        )