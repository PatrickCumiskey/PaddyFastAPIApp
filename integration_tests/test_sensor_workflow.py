"""
Integration tests for sensor-related workflows.
These tests verify the entire flow from API request to database storage and back.
"""
from fastapi.testclient import TestClient


def test_create_and_get_sensor(client: TestClient):
    """Test creating a sensor and then retrieving it."""
    # 1. Create a new sensor
    sensor_data = {
        "name": "Integration Test Sensor",
        "location": "Test Location"
    }

    create_response = client.post("/sensors/", json=sensor_data)

    # Verify the response
    assert create_response.status_code == 201, "Should return 201 Created"
    created_sensor = create_response.json()
    assert created_sensor["name"] == sensor_data["name"]
    assert created_sensor["location"] == sensor_data["location"]
    assert "id" in created_sensor

    # Get the sensor ID
    sensor_id = created_sensor["id"]

    # 2. Retrieve the sensor by ID
    get_response = client.get(f"/sensors/{sensor_id}")

    # Verify the get response
    assert get_response.status_code == 200, "Should return 200 OK"
    retrieved_sensor = get_response.json()
    assert retrieved_sensor["id"] == sensor_id
    assert retrieved_sensor["name"] == sensor_data["name"]
    assert retrieved_sensor["location"] == sensor_data["location"]

    # 3. List all sensors
    list_response = client.get("/sensors/")

    # Verify the list response
    assert list_response.status_code == 200, "Should return 200 OK"
    sensors = list_response.json()
    assert len(sensors) >= 1, "Should have at least one sensor"

    # Check if our sensor is in the list
    sensor_ids = [s["id"] for s in sensors]
    assert sensor_id in sensor_ids, "Created sensor should be in the list"


def test_get_nonexistent_sensor(client: TestClient):
    """Test retrieving a sensor that doesn't exist."""
    # Try to get a sensor with ID 999 (should not exist)
    response = client.get("/sensors/999")

    # Verify the response
    assert response.status_code == 404, "Should return 404 Not Found"
    assert "detail" in response.json()
    assert response.json()["detail"] == "Sensor not found"


def test_sensor_pagination(client: TestClient):
    """Test pagination for listing sensors."""
    # Create 5 sensors for testing pagination
    for i in range(5):
        sensor_data = {
            "name": f"Pagination Sensor {i}",
            "location": f"Location {i}"
        }
        client.post("/sensors/", json=sensor_data)

    # Test with limit=2, skip=0 (should get first 2 sensors)
    response = client.get("/sensors/?limit=2&skip=0")
    assert response.status_code == 200
    sensors = response.json()
    assert len(sensors) == 2, "Should return exactly 2 sensors"

    # Test with limit=2, skip=2 (should get next 2 sensors)
    response = client.get("/sensors/?limit=2&skip=2")
    assert response.status_code == 200
    sensors = response.json()
    assert len(sensors) == 2, "Should return exactly 2 sensors"

    # These should be different sensors than the first request
    first_page = client.get("/sensors/?limit=2&skip=0").json()
    first_page_ids = [s["id"] for s in first_page]
    second_page_ids = [s["id"] for s in sensors]

    # Check that the ids are different
    assert not any(sid in first_page_ids for sid in second_page_ids)