from random import uniform

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.models import Sensor, Metric
from src.utils.datetime_helper import get_date_range
from src.utils.helpers import get_sample_metric_ranges, generate_timestamp_range

router = APIRouter(
    prefix="/test",
    tags=["testing"]
)

@router.post("/create-sample-data/", status_code=201)
def create_sample_data(db: Session = Depends(get_db)):
    """
    Test endpoint to create a sample sensor and populate it with random weather data
    for the past week. This endpoint requires a POST request for data creation.
    """
    # Create a test sensor
    test_sensor = Sensor(
        name="Test Weather Station",
        location="Test Location"
    )
    db.add(test_sensor)
    db.commit()
    db.refresh(test_sensor)

    # Generate sample metrics for the past week
    start_date, end_date = get_date_range(days_ago=7)

    # Create a series of timestamps (one reading every 3 hours)
    timestamps = generate_timestamp_range(start_date, end_date, interval_hours=3)

    # Get sample metric ranges
    metric_ranges = get_sample_metric_ranges()

    # Generate metrics
    metrics = []
    for ts in timestamps:
        for metric_type, (min_val, max_val) in metric_ranges.items():
            value = uniform(min_val, max_val)

            metrics.append(Metric(
                sensor_id=test_sensor.id,
                metric_type=metric_type,
                value=value,
                timestamp=ts
            ))

    # Add all metrics to the database
    db.add_all(metrics)
    db.commit()

    return {
        "message": "Sample data created successfully",
        "sensor_id": test_sensor.id,
        "metrics_count": len(metrics),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }