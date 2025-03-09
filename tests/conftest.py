from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.database import Base, get_db
from src.main import app
from src.models.models import Sensor, Metric
from src.utils.datetime_helper import get_date_range

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Creates a fresh in-memory database for each test function"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Use our own database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test is done
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with a temporary database session"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Reset the overrides
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def sample_sensor(test_db):
    """Create a sample sensor for testing"""
    sensor = Sensor(name="Test Sensor", location="Test Location")
    test_db.add(sensor)
    test_db.commit()
    test_db.refresh(sensor)
    return sensor


@pytest.fixture(scope="function")
def sample_metrics(test_db, sample_sensor):
    """Create sample metrics for testing"""
    # Create metrics for the past week
    start_date, end_date = get_date_range(days_ago=7)

    # Create a reading every day
    metrics = []
    current = start_date
    while current <= end_date:
        # Add temperature reading
        metrics.append(Metric(
            sensor_id=sample_sensor.id,
            metric_type="temperature",
            value=25.0,  # Constant value for predictable testing
            timestamp=current
        ))

        # Add humidity reading
        metrics.append(Metric(
            sensor_id=sample_sensor.id,
            metric_type="humidity",
            value=60.0,  # Constant value for predictable testing
            timestamp=current
        ))

        current += timedelta(days=1)

    test_db.add_all(metrics)
    test_db.commit()

    # Refresh all metrics to get their IDs
    for metric in metrics:
        test_db.refresh(metric)

    return metrics