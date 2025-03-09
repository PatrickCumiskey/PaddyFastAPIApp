"""
Integration tests for query-related workflows.
These tests verify the query functionality with actual API requests.
"""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def setup_test_data(client):
    """Helper function to set up test data for query tests."""
    # Create two sensors
    sensors = []
    for i in range(2):
        sensor_data = {
            "name": f"Query Test Sensor {i}",
            "location": f"Location {i}"
        }
        response = client.post("/sensors/", json=sensor_data)
        sensors.append(response.json())

    # Get sensor IDs
    sensor_ids = [s["id"] for s in sensors]

    # Create metrics for both sensors
    metrics = []
    for sensor_id in sensor_ids:
        # Create temperature metrics
        temp_data = {
            "sensor_id": sensor_id,
            "metric_type": "temperature",
            "value": 25.0 + sensor_id  # Different value for each sensor
        }
        response = client.post("/metrics/", json=temp_data)
        metrics.append(response.json())

        # Create humidity metrics
        humidity_data = {
            "sensor_id": sensor_id,
            "metric_type": "humidity",
            "value": 60.0 + sensor_id  # Different value for each sensor
        }
        response = client.post("/metrics/", json=humidity_data)
        metrics.append(response.json())

    return sensor_ids, metrics

def test_query_average(client: TestClient):
    """Test querying average metrics."""
    # Setup test data
    sensor_ids, _ = setup_test_data(client)

    # Create query for average temperature across both sensors
    query_data = {
        "sensor_ids": sensor_ids,
        "metric_types": ["temperature"],
        "statistic": "avg"
    }

    # Execute query
    response = client.post("/query/", json=query_data)
    assert response.status_code == 200

    # Check result
    results = response.json()
    assert len(results) == 1, "Should have one result for temperature"

    temperature_result = results[0]
    assert temperature_result["metric_type"] == "temperature"
    assert temperature_result["statistic"] == "avg"

    # For average responses: check for MultiSensorQueryResult format
    assert "sensor_ids" in temperature_result
    assert "sensor_id" not in temperature_result  # No sensor_id field
    assert set(temperature_result["sensor_ids"]) == set(sensor_ids)

    # The average should be between the two values we set
    # (25.0 + sensor_id for each sensor)
    assert 25.0 < temperature_result["value"] < 27.0

def test_query_min_max(client: TestClient):
    """Test querying min and max metrics."""
    # Setup test data
    sensor_ids, _ = setup_test_data(client)

    # Test min query
    min_query = {
        "sensor_ids": sensor_ids,
        "metric_types": ["temperature"],
        "statistic": "min"
    }

    min_response = client.post("/query/", json=min_query)
    assert min_response.status_code == 200
    min_result = min_response.json()[0]
    assert min_result["statistic"] == "min"

    # For min responses: check for SingleSensorQueryResult format
    assert "sensor_id" in min_result
    assert "sensor_ids" not in min_result  # No sensor_ids field
    assert min_result["sensor_id"] in sensor_ids

    # Verify that this is actually the minimum value
    # by checking that the value equals the min temp for the specified sensor
    min_sensor_id = min_result["sensor_id"]
    min_value = min_result["value"]

    # Using the returned sensor ID, we can make our own API call to check:
    # Get the minimum temperature for that specific sensor
    check_query = {
        "sensor_ids": [min_sensor_id],
        "metric_types": ["temperature"],
        "statistic": "min"
    }
    check_response = client.post("/query/", json=check_query)
    assert check_response.status_code == 200
    check_result = check_response.json()[0]

    # The value should be the same as the minimum across all sensors
    assert check_result["value"] == min_value

    # Test max query
    max_query = {
        "sensor_ids": sensor_ids,
        "metric_types": ["temperature"],
        "statistic": "max"
    }

    max_response = client.post("/query/", json=max_query)
    assert max_response.status_code == 200
    max_result = max_response.json()[0]
    assert max_result["statistic"] == "max"

    # For max responses: check for SingleSensorQueryResult format
    assert "sensor_id" in max_result
    assert "sensor_ids" not in max_result  # No sensor_ids field
    assert max_result["sensor_id"] in sensor_ids

def test_weekly_averages(client: TestClient):
    """Test the weekly averages endpoint."""
    # Setup test data
    sensor_ids, _ = setup_test_data(client)

    # Get weekly averages for the first sensor
    response = client.get(f"/sensors/{sensor_ids[0]}/weekly-averages/")
    assert response.status_code == 200

    # Check results
    results = response.json()
    assert len(results) == 2, "Should have results for temperature and humidity"

    # Check that we have both metric types
    metric_types = [r["metric_type"] for r in results]
    assert "temperature" in metric_types
    assert "humidity" in metric_types

    # Check the values
    for result in results:
        if result["metric_type"] == "temperature":
            assert result["value"] == 25.0 + sensor_ids[0]
        elif result["metric_type"] == "humidity":
            assert result["value"] == 60.0 + sensor_ids[0]

def test_query_date_range(client: TestClient):
    """Test querying with a date range."""
    # Setup test data
    sensor_ids, _ = setup_test_data(client)

    # Get current time
    now = datetime.now(timezone.utc)

    # Create a date range query (past 7 days)
    query_data = {
        "sensor_ids": sensor_ids,
        "metric_types": ["temperature"],
        "statistic": "avg",
        "start_date": (now - timedelta(days=7)).isoformat(),
        "end_date": now.isoformat()
    }

    # Execute query
    response = client.post("/query/", json=query_data)
    assert response.status_code == 200

    # Our data should be within this range
    results = response.json()
    assert len(results) > 0, "Should have results"

    # Create a date range query for future dates (should return no results)
    future_query = {
        "sensor_ids": sensor_ids,
        "metric_types": ["temperature"],
        "statistic": "avg",
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=7)).isoformat()
    }

    # Execute query
    future_response = client.post("/query/", json=future_query)
    assert future_response.status_code == 200

    # Should have no results since our data is in the past
    future_results = future_response.json()
    assert len(future_results) == 0, "Should have no results for future dates"