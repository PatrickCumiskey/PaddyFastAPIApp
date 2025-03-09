"""
Integration tests for error handling scenarios.
These tests verify that the API properly handles error conditions.
"""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def test_invalid_sensor_id(client: TestClient):
    """Test that using an invalid sensor ID returns 404."""
    # Try to access a sensor that doesn't exist
    response = client.get("/sensors/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor not found"

    # Try to get weekly averages for a non-existent sensor
    response = client.get("/sensors/999/weekly-averages/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor not found"


def test_invalid_query_parameters(client: TestClient):
    """Test that providing invalid query parameters returns appropriate errors."""
    # Test with invalid date range (end before start)
    now = datetime.now(timezone.utc)
    query_data = {
        "metric_types": ["temperature"],
        "statistic": "avg",
        "start_date": now.isoformat(),
        "end_date": (now - timedelta(days=1)).isoformat()
    }

    response = client.post("/query/", json=query_data)
    assert response.status_code == 422, "Should return validation error"

    # Test with invalid metric type
    query_data = {
        "metric_types": ["invalid_metric"],
        "statistic": "avg"
    }

    response = client.post("/query/", json=query_data)
    assert response.status_code == 422, "Should return validation error"

    # Test with invalid statistic
    query_data = {
        "metric_types": ["temperature"],
        "statistic": "invalid_stat"
    }

    response = client.post("/query/", json=query_data)
    assert response.status_code == 422, "Should return validation error"


def test_missing_required_fields(client: TestClient):
    """Test that missing required fields returns appropriate errors."""
    # Missing name in sensor creation
    response = client.post("/sensors/", json={"location": "Test"})
    assert response.status_code == 422, "Should return validation error"

    # Missing sensor_id in metric creation
    response = client.post("/metrics/", json={"metric_type": "temperature", "value": 25.0})
    assert response.status_code == 422, "Should return validation error"

    # Missing metric_type in query
    response = client.post("/query/", json={"statistic": "avg"})
    assert response.status_code == 422, "Should return validation error"


def test_database_connection_handling():
    """Test how the application handles database connection issues."""
    # This test requires a separate client with a bad database connection
    from fastapi.testclient import TestClient
    from src.main import app
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database.database import get_db

    # Create a database connection that will fail
    INVALID_DB_URL = "sqlite:///nonexistent/path/to/db.sqlite"

    try:
        engine = create_engine(INVALID_DB_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Override the dependency to use our bad connection
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        # Create a client with the bad connection
        with TestClient(app) as client:
            # This should return a 500 error, not crash the application
            response = client.get("/sensors/")
            assert response.status_code == 500
            assert "database" in response.json()["detail"].lower()
    finally:
        # Reset the dependency override
        app.dependency_overrides = {}