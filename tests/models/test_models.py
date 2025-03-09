from datetime import datetime

from src.models.models import Sensor, Metric
from src.utils.datetime_helper import utc_now


def test_sensor_model(test_db):
    """Test creating and querying a Sensor model"""
    # Create a sensor
    sensor = Sensor(name="Test Sensor", location="Test Location")
    test_db.add(sensor)
    test_db.commit()
    test_db.refresh(sensor)

    # Verify it has an ID
    assert sensor.id is not None
    assert sensor.name == "Test Sensor"
    assert sensor.location == "Test Location"

    # Check created_at is set
    assert isinstance(sensor.created_at, datetime)

    # Query it back from the database
    queried_sensor = test_db.query(Sensor).filter(Sensor.id == sensor.id).first()
    assert queried_sensor is not None
    assert queried_sensor.name == "Test Sensor"
    assert queried_sensor.location == "Test Location"


def test_metric_model(test_db, sample_sensor):
    """Test creating and querying a Metric model"""
    # Create a metric
    metric = Metric(
        sensor_id=sample_sensor.id,
        metric_type="temperature",
        value=25.5,
        timestamp=utc_now()
    )
    test_db.add(metric)
    test_db.commit()
    test_db.refresh(metric)

    # Verify it has an ID
    assert metric.id is not None
    assert metric.sensor_id == sample_sensor.id
    assert metric.metric_type == "temperature"
    assert metric.value == 25.5
    assert isinstance(metric.timestamp, datetime)

    # Query it back from the database
    queried_metric = test_db.query(Metric).filter(Metric.id == metric.id).first()
    assert queried_metric is not None
    assert queried_metric.sensor_id == sample_sensor.id
    assert queried_metric.metric_type == "temperature"
    assert queried_metric.value == 25.5


def test_relationships(test_db, sample_sensor):
    """Test the relationships between Sensor and Metric models"""
    # Create metrics for the sensor
    metric1 = Metric(
        sensor_id=sample_sensor.id,
        metric_type="temperature",
        value=25.5,
        timestamp=utc_now()
    )
    metric2 = Metric(
        sensor_id=sample_sensor.id,
        metric_type="humidity",
        value=60.0,
        timestamp=utc_now()
    )
    test_db.add_all([metric1, metric2])
    test_db.commit()

    # Refresh the sample_sensor from database to get the metrics relationship
    test_db.refresh(sample_sensor)

    # Test relationship from sensor to metrics
    assert len(sample_sensor.metrics) == 2
    assert sample_sensor.metrics[0].metric_type in ["temperature", "humidity"]
    assert sample_sensor.metrics[1].metric_type in ["temperature", "humidity"]

    # Test relationship from metric to sensor
    test_db.refresh(metric1)
    assert metric1.sensor is not None
    assert metric1.sensor.id == sample_sensor.id
    assert metric1.sensor.name == "Test Sensor"