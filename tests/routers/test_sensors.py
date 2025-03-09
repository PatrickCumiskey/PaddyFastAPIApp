from src.models.models import Sensor


def test_create_sensor(client):
    """Test creating a sensor via the API"""
    sensor_data = {
        "name": "Garden Sensor",
        "location": "Backyard"
    }

    response = client.post("/sensors/", json=sensor_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Garden Sensor"
    assert data["location"] == "Backyard"
    assert "id" in data
    assert "created_at" in data


def test_get_sensors_empty(client):
    """Test getting all sensors when none exist"""
    response = client.get("/sensors/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_sensors(client, sample_sensor):
    """Test getting all sensors"""
    response = client.get("/sensors/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == sample_sensor.id
    assert data[0]["name"] == sample_sensor.name
    assert data[0]["location"] == sample_sensor.location


def test_get_sensor(client, sample_sensor):
    """Test getting a specific sensor"""
    response = client.get(f"/sensors/{sample_sensor.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_sensor.id
    assert data["name"] == sample_sensor.name
    assert data["location"] == sample_sensor.location


def test_get_sensor_not_found(client):
    """Test getting a sensor that doesn't exist"""
    response = client.get("/sensors/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor not found"


def test_pagination(client, test_db):
    """Test pagination in get_sensors endpoint"""
    # Create 15 sensors
    sensors = []
    for i in range(15):
        sensor = Sensor(name=f"Sensor {i}", location=f"Location {i}")
        test_db.add(sensor)

    test_db.commit()

    # Test default pagination (limit=100, skip=0)
    response = client.get("/sensors/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15

    # Test custom pagination
    response = client.get("/sensors/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["name"] == "Sensor 5"
    assert data[4]["name"] == "Sensor 9"