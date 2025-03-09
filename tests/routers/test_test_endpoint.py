from src.models.models import Sensor

def test_create_sample_data_post(client, test_db):
    """Test the POST endpoint for creating sample data"""
    response = client.post("/test/create-sample-data/")

    assert response.status_code == 201
    data = response.json()

    # Check that the response contains expected fields
    assert "message" in data
    assert "sensor_id" in data
    assert "metrics_count" in data
    assert "date_range" in data

    # Verify that a sensor was actually created
    sensor_id = data["sensor_id"]
    sensor = test_db.query(Sensor).filter(Sensor.id == sensor_id).first()
    assert sensor is not None