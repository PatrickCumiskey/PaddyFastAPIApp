"""
Integration tests for metric-related workflows.
These tests verify the creation and retrieval of metrics with actual API requests.
"""
from fastapi.testclient import TestClient


def test_create_and_get_metrics(client: TestClient):
    """Test creating metrics for a sensor and then retrieving them."""
    # 1. Create a test sensor first
    sensor_data = {
        "name": "Metric Test Sensor",
        "location": "Test Location"
    }

    create_sensor_response = client.post("/sensors/", json=sensor_data)
    assert create_sensor_response.status_code == 201
    sensor_id = create_sensor_response.json()["id"]

    # 2. Create metrics for this sensor
    metrics_data = [
        {
            "sensor_id": sensor_id,
            "metric_type": "temperature",
            "value": 25.5
        },
        {
            "sensor_id": sensor_id,
            "metric_type": "humidity",
            "value": 60.0
        }
    ]

    created_metrics = []
    for metric_data in metrics_data:
        response = client.post("/metrics/", json=metric_data)
        assert response.status_code == 201, f"Failed to create metric with data: {metric_data}"
        created_metrics.append(response.json())

    # 3. Get all metrics
    get_metrics_response = client.get("/metrics/")
    assert get_metrics_response.status_code == 200
    all_metrics = get_metrics_response.json()
    assert len(all_metrics) >= 2, "Should have at least the two metrics we created"

    # Check if our metrics are in the list
    created_metric_ids = [m["id"] for m in created_metrics]
    retrieved_metric_ids = [m["id"] for m in all_metrics]

    for metric_id in created_metric_ids:
        assert metric_id in retrieved_metric_ids, "Created metric should be in the list"

    # 4. Get metrics for our specific sensor
    get_sensor_metrics_response = client.get(f"/metrics/?sensor_id={sensor_id}")
    assert get_sensor_metrics_response.status_code == 200
    sensor_metrics = get_sensor_metrics_response.json()
    assert len(sensor_metrics) == 2, "Should have exactly two metrics for our sensor"

    # Check metric values
    metric_values = {m["metric_type"]: m["value"] for m in sensor_metrics}
    assert "temperature" in metric_values
    assert "humidity" in metric_values
    assert metric_values["temperature"] == 25.5
    assert metric_values["humidity"] == 60.0


def test_create_metric_invalid_sensor(client: TestClient):
    """Test creating a metric for a sensor that doesn't exist."""
    # Try to create a metric for a nonexistent sensor
    metric_data = {
        "sensor_id": 999,  # This ID should not exist
        "metric_type": "temperature",
        "value": 25.5
    }

    response = client.post("/metrics/", json=metric_data)
    assert response.status_code == 404, "Should return 404 Not Found"
    assert response.json()["detail"] == "Sensor not found"


def test_create_metric_invalid_type(client: TestClient):
    """Test creating a metric with an invalid type."""
    # 1. Create a test sensor first
    sensor_data = {
        "name": "Invalid Metric Test Sensor",
        "location": "Test Location"
    }

    create_sensor_response = client.post("/sensors/", json=sensor_data)
    assert create_sensor_response.status_code == 201
    sensor_id = create_sensor_response.json()["id"]

    # 2. Try to create a metric with an invalid type
    metric_data = {
        "sensor_id": sensor_id,
        "metric_type": "invalid_type",  # Not in our enum
        "value": 25.5
    }

    response = client.post("/metrics/", json=metric_data)
    assert response.status_code == 422, "Should return 422 Unprocessable Entity"
    # The error should be about the invalid metric type
    assert "metric_type" in response.json()["detail"][0]["loc"]