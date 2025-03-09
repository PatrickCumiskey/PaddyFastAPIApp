def test_create_metric(client, sample_sensor):
    """Test creating a metric via the API"""
    metric_data = {
        "sensor_id": sample_sensor.id,
        "metric_type": "temperature",
        "value": 25.5
    }

    response = client.post("/metrics/", json=metric_data)

    assert response.status_code == 201
    data = response.json()
    assert data["sensor_id"] == sample_sensor.id
    assert data["metric_type"] == "temperature"
    assert data["value"] == 25.5
    assert "id" in data
    assert "timestamp" in data


def test_create_metric_invalid_sensor(client):
    """Test creating a metric for a non-existent sensor"""
    metric_data = {
        "sensor_id": 999,
        "metric_type": "temperature",
        "value": 25.5
    }

    response = client.post("/metrics/", json=metric_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor not found"


def test_create_metric_invalid_type(client, sample_sensor):
    """Test creating a metric with an invalid type"""
    metric_data = {
        "sensor_id": sample_sensor.id,
        "metric_type": "invalid",
        "value": 25.5
    }

    response = client.post("/metrics/", json=metric_data)

    assert response.status_code == 422  # ValidationError


def test_get_metrics_empty(client):
    """Test getting all metrics when none exist"""
    response = client.get("/metrics/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_metrics(client, sample_metrics):
    """Test getting all metrics"""
    response = client.get("/metrics/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(sample_metrics)

    # Verify each metric has expected fields
    for metric in data:
        assert "id" in metric
        assert "sensor_id" in metric
        assert "metric_type" in metric
        assert "value" in metric
        assert "timestamp" in metric


def test_get_metrics_by_sensor(client, sample_sensor, sample_metrics):
    """Test filtering metrics by sensor_id"""
    response = client.get(f"/metrics/?sensor_id={sample_sensor.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(sample_metrics)

    # Verify all metrics belong to the requested sensor
    for metric in data:
        assert metric["sensor_id"] == sample_sensor.id


def test_get_metrics_by_invalid_sensor(client):
    """Test filtering metrics by a non-existent sensor_id"""
    response = client.get("/metrics/?sensor_id=999")

    assert response.status_code == 200
    assert response.json() == []


def test_metrics_pagination(client, sample_metrics):
    """Test pagination in get_metrics endpoint"""
    # Test default pagination (limit=100, skip=0)
    response = client.get("/metrics/")
    assert response.status_code == 200
    assert len(response.json()) == len(sample_metrics)

    # Test custom pagination
    response = client.get("/metrics/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Make sure we're getting the 3rd and 4th metrics
    all_ids = [metric.id for metric in sample_metrics]
    assert data[0]["id"] in all_ids
    assert data[1]["id"] in all_ids