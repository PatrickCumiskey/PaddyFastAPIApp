from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.models import Metric, Sensor
from src.schemas.schemas import MetricCreate, MetricResponse

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"]
)


@router.post("/", response_model=MetricResponse, status_code=201)
def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    # Check if sensor exists
    sensor = db.query(Sensor).filter(Sensor.id == metric.sensor_id).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db_metric = Metric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.get("/", response_model=List[MetricResponse])
def get_metrics(
        skip: int = 0,
        limit: int = 100,
        sensor_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Metric)
    if sensor_id:
        query = query.filter(Metric.sensor_id == sensor_id)
    metrics = query.offset(skip).limit(limit).all()
    return metrics